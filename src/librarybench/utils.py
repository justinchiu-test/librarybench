"""Utility functions for code generation and improvement."""

import re
from typing import Optional, Dict, List, Any
from librarybench.types import StdinStdoutDict

def extract_code(solution: str, model_type: Optional[str] = None) -> str:
    """
    Extract code from model solutions.

    Args:
        solution: String containing the model's solution
        model_type: Optional string indicating the model type ('openai' or 'claude')
                   If None, will try to detect from solution format

    Returns:
        The extracted code
    """
    # Auto-detect model type based on solution patterns if not provided
    if model_type is None:
        # Check for OpenAI's dash pattern (more specific)
        dashed_code_pattern = r"[-]{5,}\n(.*?)[-]{5,}"
        if re.search(dashed_code_pattern, solution, re.DOTALL):
            model_type = "openai"
        else:
            # Default to Claude-style extraction (which is more general)
            model_type = "claude"

    if model_type == "openai":
        # For O3 mini solutions, try to extract code between dashed lines
        dashed_code_pattern = r"[-]{5,}\n(.*?)[-]{5,}"
        match = re.search(dashed_code_pattern, solution, re.DOTALL)
        if match:
            return match.group(1)

        # Try to extract code between ```python and ``` markers
        code_pattern = r"```python\n(.*?)\n```"
        match = re.search(code_pattern, solution, re.DOTALL)
        if match:
            return match.group(1)
    else:  # claude
        # Try to extract code between ```python and ``` markers (Claude's standard format)
        code_pattern = r"```python\n(.*?)\n```"
        match = re.search(code_pattern, solution, re.DOTALL)
        if match:
            return match.group(1)

        # If no python markers found, try with any language marker
        code_pattern = r"```(?:\w+)?\n(.*?)\n```"
        match = re.search(code_pattern, solution, re.DOTALL)
        if match:
            return match.group(1)

    # If no markers found, try to extract the first code-like block (works for both models)
    code_pattern = r"class .*?:|def .*?:"
    match = re.search(code_pattern, solution)
    if match:
        # Get the position of the match
        start_pos = match.start()
        # Extract from this position to the end
        return solution[start_pos:]

    return solution


def create_test_cases_from_input_output(
    input_output: dict,
) -> List[StdinStdoutDict]:
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
    test_cases: List[StdinStdoutDict],
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
        status = "✅ PASSED" if result.get("passed", False) else "❌ FAILED"
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
