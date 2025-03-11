"""Streamlit app to visualize solutions from JSON files."""

import json
import streamlit as st
from typing import Dict, List, Any, Optional

# Set page configuration
st.set_page_config(
    page_title="Library Bench Solution Visualizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Style
st.markdown(
    """
<style>
    .problem-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .solution-container {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .test-results {
        display: flex;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }
    .test-pass {
        color: green;
        font-weight: bold;
    }
    .test-fail {
        color: red;
        font-weight: bold;
    }
    .solution-stats {
        display: flex;
        gap: 1rem;
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


def load_solution_file(file_path: str) -> List[Dict[str, Any]]:
    """Load solution data from a JSON file."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return []


def display_solution(solution: Dict[str, Any], index: int):
    """Display a single solution with details."""
    # Extract data
    problem = solution.get("problem", {})
    problem_id = problem.get("problem_id", index)
    source = problem.get("source", "Unknown")
    difficulty = problem.get("difficulty", "Unknown")
    question = problem.get("question", "")
    code = solution.get("code", "")
    tests_passed = solution.get("tests_passed", 0)
    tests_total = solution.get("tests_total", 0)
    pass_ratio = solution.get("pass_ratio", 0.0)
    model_name = solution.get("model_name", "Unknown")
    iterations = solution.get("iterations", 1)
    history = solution.get("history", [])

    # Create expandable section for this solution
    with st.expander(
        f"Problem {problem_id}: {source} (Difficulty: {difficulty})",
        expanded=index == 0,
    ):
        # Display solution stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Tests Passed", f"{tests_passed}/{tests_total}")
        with col2:
            st.metric("Pass Ratio", f"{pass_ratio:.2%}")
        with col3:
            st.metric("Model", model_name)
        with col4:
            st.metric("Iterations", iterations)

        # Problem description and test cases in tabs
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Problem", "Solution", "Test Cases", "Iteration History"]
        )

        with tab1:
            st.markdown(question)

        with tab2:
            st.code(code, language="python")

            if st.button("Copy Code", key=f"copy_{index}"):
                st.toast("Code copied to clipboard!")
                st.session_state[f"copied_{index}"] = True

        with tab3:
            tests = problem.get("tests", [])
            if tests:
                for i, test in enumerate(tests):
                    st.markdown(f"**Test {i + 1}:**")
                    st.markdown("**Input:**")
                    st.code(test.get("stdin", ""))
                    st.markdown("**Expected Output:**")
                    st.code(test.get("stdout", ""))
                    st.divider()
            else:
                st.info("No test cases available")

        with tab4:
            if history:
                for i, entry in enumerate(history):
                    iteration = entry.get("iteration", i)
                    iter_code = entry.get("code", "")
                    iter_pass_ratio = entry.get("pass_ratio", 0.0)
                    iter_tests_passed = entry.get("tests_passed", 0)
                    iter_tests_total = entry.get("tests_total", 0)

                    st.markdown(f"**Iteration {iteration}**")
                    st.markdown(
                        f"Pass ratio: {iter_pass_ratio:.2%} ({iter_tests_passed}/{iter_tests_total})"
                    )
                    with st.expander("Code", expanded=False):
                        st.code(iter_code, language="python")
                    st.divider()
            else:
                st.info("No iteration history available")


def main():
    """Main entry point for the Streamlit app."""
    st.title("Library Bench Solution Visualizer")

    # Sidebar for file selection
    st.sidebar.header("Settings")

    # Default file path
    default_path = "data/o3_mini_chess_solutions_improved.json"

    # File path input
    file_path = st.sidebar.text_input("Solution file path", value=default_path)

    # Load solutions
    if file_path:
        solutions = load_solution_file(file_path)

        if solutions:
            # Display summary
            st.write(f"Found {len(solutions)} solutions")

            # Calculate overall stats
            total_tests_passed = sum(s.get("tests_passed", 0) for s in solutions)
            total_tests = sum(s.get("tests_total", 0) for s in solutions)
            overall_pass_ratio = (
                total_tests_passed / total_tests if total_tests > 0 else 0
            )

            # Display overall metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Solutions", len(solutions))
            with col2:
                st.metric("Overall Pass Ratio", f"{overall_pass_ratio:.2%}")
            with col3:
                st.metric("Total Tests Passed", f"{total_tests_passed}/{total_tests}")

            st.divider()

            # Filter options
            st.sidebar.header("Filters")

            # Get all available sources and difficulties
            sources = sorted(
                set(s.get("problem", {}).get("source", "Unknown") for s in solutions)
            )
            difficulties = sorted(
                set(
                    s.get("problem", {}).get("difficulty", "Unknown") for s in solutions
                )
            )

            # Filter by source
            selected_sources = st.sidebar.multiselect(
                "Filter by source", options=sources, default=sources
            )

            # Filter by difficulty
            selected_difficulties = st.sidebar.multiselect(
                "Filter by difficulty", options=difficulties, default=difficulties
            )

            # Apply filters
            filtered_solutions = [
                s
                for s in solutions
                if s.get("problem", {}).get("source", "Unknown") in selected_sources
                and s.get("problem", {}).get("difficulty", "Unknown")
                in selected_difficulties
            ]

            # Sort options
            sort_options = {
                "Problem ID": lambda s: s.get("problem", {}).get("problem_id", 0),
                "Source": lambda s: s.get("problem", {}).get("source", "Unknown"),
                "Difficulty": lambda s: s.get("problem", {}).get(
                    "difficulty", "Unknown"
                ),
                "Pass Ratio (High to Low)": lambda s: -s.get("pass_ratio", 0),
                "Pass Ratio (Low to High)": lambda s: s.get("pass_ratio", 0),
                "Iterations": lambda s: s.get("iterations", 1),
            }

            sort_by = st.sidebar.selectbox(
                "Sort by", options=list(sort_options.keys()), index=0
            )

            # Sort solutions
            sorted_solutions = sorted(filtered_solutions, key=sort_options[sort_by])

            # Display solutions
            if sorted_solutions:
                st.write(f"Showing {len(sorted_solutions)} solutions")

                for i, solution in enumerate(sorted_solutions):
                    display_solution(solution, i)
            else:
                st.warning("No solutions match the selected filters")
        else:
            st.error(f"No solutions found in file: {file_path}")


if __name__ == "__main__":
    main()
