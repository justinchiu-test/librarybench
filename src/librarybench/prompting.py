"""Prompt generation module for solution generation and improvement."""

import json
from typing import Dict, Any, List

from librarybench.types import Problem


def format_generation_prompt(example: Problem) -> str:
    """Format the problem for initial solution generation.

    Args:
        example: Problem example with metadata

    Returns:
        Formatted prompt for the model
    """
    # Parse input_output field to extract test cases
    input_output = example.tests

    # Extract the first test case for the prompt
    first_input = input_output[0].stdin
    first_output = input_output[0].stdout

    # Construct the prompt
    prompt = f"""You are an expert Python programmer. Your task is to solve a coding problem.

Problem statement:
{example.question}

Write a Python solution that solves this problem. The solution should be efficient and handle all edge cases.

Example Input:
{first_input}

Example Output:
{first_output}

Implement your solution wrapped in markdown:
```python
...
```"""

    return prompt


def format_improvement_prompt(
    problem: Problem,
    original_code: str,
    test_results: List[Dict[str, Any]],
    passed: int,
    total: int,
) -> str:
    """Format the improvement prompt with test results.

    Args:
        problem: Original problem data
        original_code: The code that needs improvement
        test_results: Results from test runs
        stdin_stdout_tests: The test cases
        passed: Number of passed tests
        total: Total number of tests

    Returns:
        Formatted improvement prompt
    """
    # Format feedback for the model
    from librarybench.utils import format_feedback

    feedback = format_feedback(test_results, problem.tests, passed, total)

    prompt = f"""You are an expert Python programmer. Your task is to fix a solution to a coding problem.

Problem statement:
{problem.question}

The current solution is:
```python
{original_code}
```

This solution is failing on some test cases. Here are the test results:

{feedback}

Please rewrite the solution to fix the issues and make it pass all the test cases.
Focus on correctness first, then efficiency. Make sure to handle all edge cases.

Return the improved solution wrapped in markdown:
```python
...
```"""

    return prompt
