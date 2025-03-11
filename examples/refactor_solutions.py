"""Example workflow for refactoring multiple solutions into a single implementation."""

import os
import json
import asyncio
import argparse
from typing import List

from librarybench.models import ClaudeClient
from librarybench.llm import query_model
from librarybench.types import SolutionResult
from librarybench.execution import evaluate_solution
from librarybench.utils import extract_code


async def load_solutions(file_path: str) -> List[SolutionResult]:
    """Load solutions from a JSON file.

    Args:
        file_path: Path to solution JSON file

    Returns:
        List of SolutionResult objects
    """
    with open(file_path, "r") as f:
        solutions_data = json.load(f)

    return [SolutionResult.model_validate(solution) for solution in solutions_data]


async def create_refactor_prompt(solutions: List[SolutionResult]) -> str:
    """Create a prompt for refactoring multiple solutions.

    Args:
        solutions: List of solution results to refactor

    Returns:
        Formatted prompt for the LLM
    """
    prompt = "# Refactoring Task\n\n"
    prompt += "You are tasked with refactoring multiple chess-related solutions into a single, cohesive implementation.\n\n"
    prompt += "Please create a unified solution that handles all the following problems while passing all test cases:\n\n"

    for i, solution in enumerate(solutions):
        prompt += f"## Problem {i + 1}: {solution.problem.source}\n\n"
        prompt += f"### Problem Description\n{solution.problem.question}\n\n"
        prompt += "### Test Cases\n"

        for j, test in enumerate(solution.problem.tests):
            prompt += f"Test {j + 1}:\n"
            prompt += f"Input: {test.stdin}\n"
            prompt += f"Expected Output: {test.stdout}\n\n"

        prompt += "### Current Solution\n"
        prompt += f"```python\n{solution.code}\n```\n\n"

        # Add pass stats
        prompt += f"This solution currently passes {solution.tests_passed}/{solution.tests_total} tests.\n\n"
        prompt += "---\n\n"

    prompt += """
## Refactoring Instructions

1. Create a **single unified implementation** that handles all the problems above
2. The implementation should have a main function that reads input and determines which problem solver to call
3. Refactor common functionality to reduce code duplication
4. Ensure the solution passes all test cases for all problems
5. Maintain or improve the efficiency of the original solutions
6. Provide clear function names and add helpful comments

Your solution should handle the input format properly and output the expected result for each problem. The code should be able to detect which problem is being presented based on the input pattern.

Please provide your refactored solution in Python code format.
"""

    return prompt


async def refactor_solutions(
    solution_file: str,
    output_file: str,
    cyber_url: str,
    model_name: str = "claude-3-haiku-20240307",
    num_solutions: int = 5,
) -> None:
    """Refactor multiple solutions into a single implementation.

    Args:
        solution_file: Path to solution JSON file
        output_file: Path to save the refactored solution
        cyber_url: URL for code execution API
        model_name: LLM model to use for refactoring
        num_solutions: Number of solutions to include in refactoring
    """
    # Load solutions
    solutions = await load_solutions(solution_file)
    print(f"Loaded {len(solutions)} solutions")

    # Take specified number of solutions
    solutions = solutions[:num_solutions]
    print(f"Using {len(solutions)} solutions for refactoring")

    # Create Claude client
    llm_client = ClaudeClient(model=model_name)
    print(f"Using {llm_client.model_name} for refactoring")

    # Create refactoring prompt
    prompt = await create_refactor_prompt(solutions)

    # Query model for refactored solution
    print("Requesting refactored solution from LLM...")
    response = await query_model(
        prompt=prompt,
        llm_client=llm_client,
        system_prompt="You are an expert Python programmer specializing in algorithm optimization and code refactoring.",
    )

    # Extract code from response
    refactored_code = extract_code(response)

    if not refactored_code:
        print("Failed to extract code from LLM response")
        return

    # Save refactored code
    with open(output_file, "w") as f:
        f.write(refactored_code)
    print(f"Refactored solution saved to {output_file}")

    # Evaluate refactored solution against all test cases
    print("\nEvaluating refactored solution against all test cases...")
    all_tests_passed = True
    total_passed = 0
    total_tests = 0

    for i, solution in enumerate(solutions):
        print(f"\nTesting Problem {i + 1}: {solution.problem.source}")

        # Evaluate against this problem's test cases
        evaluation = await evaluate_solution(
            refactored_code, solution.problem.tests, cyber_url
        )

        # Update counts
        passed = evaluation["tests_passed"]
        total = evaluation["tests_total"]
        passed_ratio = evaluation["pass_ratio"]
        total_passed += passed
        total_tests += total

        # Report results
        print(f"  Passed {passed}/{total} tests ({passed_ratio:.2%})")

        if passed < total:
            all_tests_passed = False

    # Summary
    overall_pass_ratio = total_passed / total_tests if total_tests > 0 else 0
    print(
        f"\nOverall Results: {total_passed}/{total_tests} tests passed ({overall_pass_ratio:.2%})"
    )

    if all_tests_passed:
        print("\n✅ Success! The refactored solution passes all test cases.")
    else:
        print("\n⚠️ The refactored solution doesn't pass all test cases.")


async def main(args):
    """Main entry point for the refactoring workflow."""
    # Check environment variables
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

    cyber_url = os.environ.get("CYBER_URL")
    if not cyber_url:
        raise ValueError("CYBER_URL environment variable is not set")

    # Run refactoring workflow
    await refactor_solutions(
        solution_file=args.solution_file,
        output_file=args.output_file,
        cyber_url=cyber_url,
        model_name=args.model_name,
        num_solutions=args.num_solutions,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Refactor multiple solutions into a single implementation"
    )
    parser.add_argument(
        "--solution-file",
        type=str,
        default="data/o3_mini_chess_solutions_improved.json",
        help="Path to JSON file with solutions",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="data/refactored_solution.py",
        help="Path to save the refactored solution",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="claude-3-haiku-20240307",
        help="Claude model to use for refactoring",
    )
    parser.add_argument(
        "--num-solutions",
        type=int,
        default=5,
        help="Number of solutions to include in refactoring",
    )

    args = parser.parse_args()
    asyncio.run(main(args))
