"""Example workflow for refactoring multiple solutions into a single implementation."""

import os
import json
import asyncio
import argparse
from typing import List, Dict, Any

from librarybench.models import ClaudeClient, OpenAiClient
from librarybench.llm import query_model
from librarybench.types import SolutionResult
from librarybench.execution import evaluate_solution
from librarybench.utils import extract_code
from librarybench.logprobs import get_log_probabilities


def load_solutions(file_path: str) -> List[SolutionResult]:
    """Load solutions from a JSON file.

    Args:
        file_path: Path to solution JSON file

    Returns:
        List of SolutionResult objects
    """
    with open(file_path, "r") as f:
        solutions_data = json.load(f)

    return [SolutionResult.model_validate(solution) for solution in solutions_data]


def create_refactor_prompt(solutions: List[SolutionResult]) -> str:
    """Create a prompt for refactoring multiple solutions.

    Args:
        solutions: List of solution results to refactor

    Returns:
        Formatted prompt for the LLM
    """
    prompt = "# Refactoring Task\n\n"
    prompt += "You are tasked with refactoring multiple solutions into a single, cohesive implementation.\n"
    prompt += "Please create a unified solution that handles all the following problems while passing all test cases.\n"
    prompt += "Make the code as concise as possible by writing library functions that are shared across all problems.\n\n"
    # prompt += "For example, start with a class Chessboard, which represents the state as a 2D numpy matrix.\n\n"

    for i, solution in enumerate(solutions):
        prompt += f"## Problem {i + 1}: {solution.problem.source}\n\n"
        prompt += f"### Problem Description\n{solution.problem.question}\n\n"
        prompt += "### Test Cases\n"

        for j, test in enumerate(solution.problem.tests[:5]):
            prompt += f"Test {j + 1}:\n"
            prompt += f"Input: {test.stdin}\n"
            prompt += f"Expected Output: {test.stdout}\n\n"

        prompt += "### Current Solution\n"
        prompt += f"```cpp\n{solution.code}\n```\n\n"

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

Your solution should handle the input format properly and output the expected result for each problem.
The first input line will tell you which problem to solve (int in 1, ..., 5), with the problem input following on subsequent lines.

Please provide your refactored solution in the markdown Cpp code format: ```cpp ... ```."""

    return prompt


def create_correction_prompt(
    refactored_code: str,
    solutions: List[SolutionResult],
    failed_tests: Dict[int, List[Dict[str, Any]]],
) -> str:
    """Create a prompt for correcting the refactored solution based on test feedback.

    Args:
        refactored_code: The refactored code to be corrected
        solutions: List of original solution results
        failed_tests: Dictionary mapping problem index to list of failed test results

    Returns:
        Formatted prompt for the LLM to correct the solution
    """
    prompt = "# Solution Correction Task\n\n"
    prompt += (
        "The refactored solution you previously created has some failing test cases.\n"
    )
    prompt += "Please correct the solution to address the failing tests.\n\n"

    prompt += "## Current Refactored Solution\n\n"
    prompt += f"```cpp\n{refactored_code}\n```\n\n"

    prompt += "## Failing Tests\n\n"

    for problem_idx, problem_tests in failed_tests.items():
        solution = solutions[problem_idx]
        prompt += f"### Problem {problem_idx + 1}: {solution.problem.source}\n\n"
        prompt += f"Description: {solution.problem.question}\n\n"

        for i, test_result in enumerate(problem_tests):
            test_case = solution.problem.tests[test_result.get("test_idx", i)]
            prompt += f"Test {i + 1}:\n"
            prompt += f"Input: {test_case.stdin}\n"
            prompt += f"Expected Output: {test_case.stdout}\n"
            prompt += f"Actual Output: {test_result.get('exec_output', {}).get('run_output', {}).get('stdout', 'N/A')}\n"

            # Include error information if available
            if (
                error := test_result.get("exec_output", {})
                .get("run_output", {})
                .get("stderr")
            ):
                prompt += f"Error: {error}\n"

            prompt += "\n"

    prompt += """
## Correction Instructions

1. Analyze the failing test cases and their output
2. Identify the root causes of the failures
3. Correct the refactored solution while maintaining its unified structure
4. Ensure your solution passes all test cases for all problems
5. Keep the code as efficient and concise as possible

Please provide your corrected solution in Cpp code format.
"""

    return prompt


async def refactor_solutions(
    solution_file: str,
    output_file: str,
    cyber_url: str,
    model_name: str = "o3-mini",
    model_provider: str = "openai",
    num_solutions: int = 5,
) -> None:
    """Refactor multiple solutions into a single implementation.

    Args:
        solution_file: Path to solution JSON file
        output_file: Path to save the refactored solution
        cyber_url: URL for code execution API
        model_name: LLM model to use for refactoring
        model_provider: Provider of the LLM ("openai" or "anthropic")
        num_solutions: Number of solutions to include in refactoring
    """
    # Load solutions
    solutions = load_solutions(solution_file)
    print(f"Loaded {len(solutions)} solutions")

    # Take specified number of solutions
    solutions = solutions[:num_solutions]
    print(f"Using {len(solutions)} solutions for refactoring")

    # Create LLM client based on provider
    if model_provider.lower() == "openai":
        llm_client = OpenAiClient(model=model_name)
    else:
        llm_client = ClaudeClient(model=model_name)
    print(f"Using {llm_client.model_name} ({model_provider}) for refactoring")

    # Create refactoring prompt
    prompt = create_refactor_prompt(solutions)

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
    refactored_line_count = len(refactored_code.split("\n"))
    print(f"Refactored solution saved to {output_file}")
    print(f"Refactored solution line count: {refactored_line_count}")

    original_logprobs = 0
    for solution in solutions:
        lp = await get_log_probabilities(solution.code)
        original_logprobs += sum(lp.logprobs)
    refactored_logprobs = await get_log_probabilities(refactored_code)
    refactored_logprobs = sum(refactored_logprobs.logprobs)
    print(f"Original logprobs: {original_logprobs:.3f}")
    print(f"Refactored logprobs: {refactored_logprobs:.3f}")

    # Evaluate refactored solution against all test cases
    print("\nEvaluating refactored solution against all test cases...")
    all_tests_passed = True
    total_passed = 0
    total_tests = 0
    failed_tests = {}  # Dictionary to track failing tests by problem index

    for i, solution in enumerate(solutions):
        print(f"\nTesting Problem {i + 1}: {solution.problem.source}")

        # Evaluate against this problem's test cases
        evaluation = await evaluate_solution(
            "cpp",
            refactored_code,
            [
                test.model_copy(update=dict(stdin=f"{i + 1}\n{test.stdin}"))
                for test in solution.problem.tests
            ],
            cyber_url,
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
            # Collect failing tests for this problem
            failed_tests[i] = [
                {**test, "test_idx": idx}
                for idx, test in enumerate(evaluation["results"])
                if not test.get("passed", False)
            ]

    # Summary
    overall_pass_ratio = total_passed / total_tests if total_tests > 0 else 0
    print(
        f"\nOverall Results: {total_passed}/{total_tests} tests passed ({overall_pass_ratio:.2%})"
    )

    print("Break before repair")
    # TODO: fix repair
    return
    # If some tests failed, give the model a chance to correct the solution
    if not all_tests_passed:
        print("\n⚠️ The refactored solution doesn't pass all test cases.")
        print("\nGenerating correction prompt based on test feedback...")

        # Create correction prompt with failing test information
        correction_prompt = create_correction_prompt(
            refactored_code, solutions, failed_tests
        )

        # Query model for corrected solution
        print("Requesting corrected solution from LLM...")
        correction_response = await query_model(
            prompt=correction_prompt,
            llm_client=llm_client,
            system_prompt="You are an expert Python programmer specializing in algorithm optimization and code refactoring.",
        )
        with open(output_file + ".fullresponse", "w") as f:
            f.write(correction_response)

        # Extract corrected code
        corrected_code = extract_code(correction_response)

        if not corrected_code:
            print("Failed to extract corrected code from LLM response")
        else:
            # Save corrected code
            with open(output_file, "w") as f:
                f.write(corrected_code)
            corrected_line_count = len(corrected_code.split("\n"))
            print(f"Corrected solution saved to {output_file}")
            print(f"Corrected solution line count: {corrected_line_count}")

            # Re-evaluate corrected solution
            print("\nRe-evaluating corrected solution against all test cases...")
            corrected_all_passed = True
            corrected_total_passed = 0

            for i, solution in enumerate(solutions):
                print(f"\nTesting Problem {i + 1}: {solution.problem.source}")

                # Evaluate against this problem's test cases
                corrected_evaluation = await evaluate_solution(
                    corrected_code, solution.problem.tests, cyber_url
                )

                # Update counts
                corrected_passed = corrected_evaluation["tests_passed"]
                corrected_total = corrected_evaluation["tests_total"]
                corrected_ratio = corrected_evaluation["pass_ratio"]
                corrected_total_passed += corrected_passed

                # Report results
                print(
                    f"  Passed {corrected_passed}/{corrected_total} tests ({corrected_ratio:.2%})"
                )

                if corrected_passed < corrected_total:
                    corrected_all_passed = False

            # Summary of correction
            corrected_overall_ratio = (
                corrected_total_passed / total_tests if total_tests > 0 else 0
            )
            print(
                f"\nCorrected Results: {corrected_total_passed}/{total_tests} tests passed ({corrected_overall_ratio:.2%})"
            )

            if corrected_all_passed:
                print("\n✅ Success! The corrected solution passes all test cases.")
            else:
                print("\n⚠️ The corrected solution still doesn't pass all test cases.")

            # Use the corrected code for the final metrics
            refactored_code = corrected_code
            refactored_line_count = corrected_line_count
    else:
        print("\n✅ Success! The refactored solution passes all test cases.")

    # Print line count comparison
    # Get the original solutions line count from solutions data
    original_line_count = sum(len(solution.code.split("\n")) for solution in solutions)
    refactored_line_count = len(refactored_code.split("\n"))
    print("\nLine count comparison:")
    print(f"Original solutions total: {original_line_count} lines")
    print(f"Refactored solution: {refactored_line_count} lines")
    print(f"Difference: {refactored_line_count - original_line_count} lines")



async def main(args):
    """Main entry point for the refactoring workflow."""
    # Check environment variables based on model provider
    if args.model_provider.lower() == "openai":
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is not set")
    else:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

    cyber_url = os.environ.get("CYBER_URL")
    if not cyber_url:
        raise ValueError("CYBER_URL environment variable is not set")

    # Count the number of code lines in the original solutions (first 5)
    original_line_count = 0
    if args.solution_file.endswith(".json"):
        with open(args.solution_file, "r") as f:
            solutions_data = json.load(f)
        original_line_count = sum(
            len(sol["code"].split("\n")) for sol in solutions_data[: args.num_solutions]
        )
        print(
            f"Original solutions line count (first {args.num_solutions}): {original_line_count}"
        )

    # check pass rate of original code
    solutions = load_solutions(args.solution_file)
    for i, solution in enumerate(solutions):
        print(f"Evaluating solution {i}")
        evaluation = await evaluate_solution(
            "cpp",
            solution.code,
            solution.problem.tests,
            cyber_url,
        )
        # Update counts
        passed = evaluation["tests_passed"]
        total = evaluation["tests_total"]
        passed_ratio = evaluation["pass_ratio"]
        # Report results
        print(f"  Passed {passed}/{total} tests ({passed_ratio:.2%})")

    # Run refactoring workflow
    await refactor_solutions(
        solution_file=args.solution_file,
        output_file=args.output_file,
        cyber_url=cyber_url,
        model_name=args.model_name,
        model_provider=args.model_provider,
        num_solutions=args.num_solutions,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Refactor multiple solutions into a single implementation"
    )
    parser.add_argument(
        "--solution-file",
        type=str,
        default="data/saved_graph_solutions_from_descriptions.json",
        help="Path to JSON file with problems",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default="data/refactored_graph_solution.py",
        help="Path to save the refactored solution",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="o3-mini",
        help="Model to use for refactoring",
    )
    parser.add_argument(
        "--model-provider",
        type=str,
        default="openai",
        choices=["openai", "anthropic"],
        help="Provider of the LLM (openai or anthropic)",
    )
    parser.add_argument(
        "--num-solutions",
        type=int,
        default=5,
        help="Number of solutions to include in refactoring",
    )

    args = parser.parse_args()
    asyncio.run(main(args))
