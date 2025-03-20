import json
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from librarybench.types import ProblemDescriptions

st.set_page_config(
    page_title="CodeContest Descriptions Explorer",
    page_icon="📊",
    layout="wide",
)

st.title("CodeContest Descriptions Explorer")

@st.cache_data
def load_data():
    path = Path("data/codecontests_graph_descriptions.json")
    with open(path, "r") as f:
        raw_problems = json.load(f)
    
    problems = [ProblemDescriptions.model_validate(x) for x in raw_problems]
    return problems

problems = load_data()

# Sidebar for filtering
st.sidebar.header("Filters")
difficulty_options = list(set(p.problem.difficulty for p in problems))
selected_difficulty = st.sidebar.multiselect(
    "Difficulty", 
    options=difficulty_options,
    default=difficulty_options,
)

source_options = list(set(p.problem.source for p in problems))
selected_source = st.sidebar.multiselect(
    "Source", 
    options=source_options,
    default=source_options,
)

# Filter data based on selection
filtered_problems = [
    p for p in problems
    if p.problem.difficulty in selected_difficulty
    and p.problem.source in selected_source
]

# Display statistics
st.header("Dataset Statistics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Problems", len(problems))
col2.metric("Filtered Problems", len(filtered_problems))
col3.metric("Avg Descriptions per Problem", np.mean([len(p.descriptions) for p in problems]).round(2))

# Problem explorer
st.header("Problem Explorer")
problem_options = [f"{p.problem.problem_id}: {p.problem.question[:50]}..." for p in filtered_problems]
selected_problem_idx = st.selectbox("Select Problem", range(len(problem_options)), format_func=lambda x: problem_options[x])

if selected_problem_idx is not None and filtered_problems:
    selected_problem = filtered_problems[selected_problem_idx]
    
    st.subheader(f"Problem #{selected_problem.problem.problem_id}")
    
    # Problem details
    st.markdown(f"**Source:** {selected_problem.problem.source}")
    st.markdown(f"**Difficulty:** {selected_problem.problem.difficulty}")
    st.markdown(f"**Language:** {selected_problem.problem.language}")
    
    # Full problem description
    with st.expander("Full Problem Description", expanded=True):
        st.markdown(selected_problem.problem.question)
    
    # Descriptions
    st.subheader("Generated Descriptions")
    for i, desc in enumerate(selected_problem.descriptions):
        with st.expander(f"Description #{i+1}", expanded=i==0):
            st.markdown(desc)
    
    # Tests
    st.subheader("Test Cases")
    test_df = pd.DataFrame([
        {"Input": test.stdin, "Expected Output": test.stdout}
        for test in selected_problem.problem.tests
    ])
    st.dataframe(test_df, use_container_width=True)
    
    # Human solutions
    st.subheader("Human Solutions")
    for i, solution in enumerate(selected_problem.problem.human_solutions):
        with st.expander(f"Solution #{i+1}"):
            st.code(solution, language=selected_problem.problem.language.lower())

else:
    st.info("No problems found with the selected filters.")

# Additional analysis
st.header("Dataset Analysis")

# Description length statistics
description_lengths = [len(desc) for problem in problems for desc in problem.descriptions]


st.subheader("Description Length Distribution")
hist_values = np.histogram(description_lengths, bins=30)[0]
st.bar_chart(pd.DataFrame(hist_values))

# Word count in descriptions
word_counts = [len(desc.split()) for problem in problems for desc in problem.descriptions]
avg_word_count = np.mean(word_counts).round(2)
st.metric("Average Word Count in Descriptions", avg_word_count)

# Source distribution
source_counts = pd.Series([p.problem.source for p in problems]).value_counts()
st.subheader("Problem Sources")
st.bar_chart(source_counts)

# Difficulty distribution
difficulty_counts = pd.Series([str(p.problem.difficulty) for p in problems]).value_counts()
st.subheader("Problem Difficulty Distribution")
st.bar_chart(difficulty_counts)

if __name__ == "__main__":
    # This is used when running the script directly
    pass
