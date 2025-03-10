"""Feedback generation module for LibraryBench."""

import json
from typing import Any, Dict, List, Optional, Tuple

from librarybench.utils import extract_code
from librarybench.execution import run_unit_tests


def create_test_cases_from_input_output(
    input_output: Dict[str, Any],
) -> List[Dict[str, str]]:
    """Convert input-output pairs to test cases for execution.

    Args:
        input_output: Dictionary with inputs and outputs lists

    Returns:
        List of test cases formatted for execution
    """
    stdin_stdout_tests = []
    if "inputs" in input_output and "outputs" in input_output:
        for inp, out in zip(input_output["inputs"], input_output["outputs"]):
            stdin_stdout_tests.append({"stdin": inp, "stdout": out})
    return stdin_stdout_tests


def format_feedback(
    test_results: List[Dict[str, Any]],
    test_cases: List[Dict[str, str]],
    passed_count: int,
    total_count: int,
) -> str:
    """Format test results as feedback for the model.

    Args:
        test_results: List of test result objects
        test_cases: List of input/output test cases
        passed_count: Number of passed tests
        total_count: Total number of tests

    Returns:
        Formatted feedback string
    """
    feedback = f"Test Results: {passed_count}/{total_count} tests passed\n\n"

    for i, (test, result) in enumerate(zip(test_cases, test_results), 1):
        status = " PASSED" if result.get("passed", False) else "L FAILED"
        feedback += f"Test #{i}: {status}\n"
        feedback += f"Input:\n{test['stdin']}\n"
        feedback += f"Expected Output:\n{test['stdout']}\n"

        if not result.get("passed", False):
            stdout = (
                result.get("exec_output", {}).get("run_output", {}).get("stdout", "")
            )
            stderr = (
                result.get("exec_output", {}).get("run_output", {}).get("stderr", "")
            )
            feedback += f"Actual Output:\n{stdout}\n"
            if stderr:
                feedback += f"Error:\n{stderr}\n"

        feedback += "-" * 40 + "\n"

    return feedback


def get_model_feedback(
    solution_file: str,
    problem_id: Optional[int] = None,
    model_name: Optional[str] = None,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Get feedback for a specific model solution.

    Args:
        solution_file: Path to the solution JSON file
        problem_id: ID of the problem to get feedback for (optional)
        model_name: Name of the model (e.g., 'claude' or 'o3_mini')

    Returns:
        Tuple of (feedback string, detailed test results)
    """
    # Load solutions
    with open(solution_file, "r") as f:
        solutions = json.load(f)

    # If problem_id specified, filter to that problem
    if problem_id is not None:
        solutions = [solutions[problem_id]]

    # Track all feedbacks
    all_feedbacks = []
    all_results = []

    for solution_data in solutions:
        stdin_stdout_tests = solution_data.get("tests")
        stdin_stdout_tests = json.loads(stdin_stdout_tests)
        model_code = extract_code(solution_data.get("code", ""))
        # Run code against test cases
        model_results = run_unit_tests([model_code], stdin_stdout_tests)

        # Calculate passed tests
        model_results_flat = model_results[0] if model_results else []
        passed = sum(1 for result in model_results_flat if result.get("passed", False))
        total = len(stdin_stdout_tests)

        # Format feedback
        feedback = format_feedback(
            model_results_flat, stdin_stdout_tests, passed, total
        )

        all_feedbacks.append(feedback)
        all_results.append(model_results_flat)

    return "\n".join(all_feedbacks), all_results
