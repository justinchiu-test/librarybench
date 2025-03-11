"""Example workflow demonstrating the LibraryBench pipeline."""

import os
import asyncio
import argparse
from typing import Optional

from librarybench import solution_process, BatchResult
from librarybench.execution import evaluate_solutions_async
from librarybench.analysis.model_comparison import (
    compare_solutions,
    print_comparison_results,
)


async def run_workflow(
    model_type: str = "claude",
    model_name: Optional[str] = None,
    sample_size: int = 3,
    problem_types: list = ["chess"],
    max_iterations: int = 2,
    output_dir: str = "data",
):
    """Run the full LibraryBench workflow using the unified processor.

    Args:
        model_type: Type of model to use ("openai" or "claude")
        model_name: Specific model name (optional)
        sample_size: Number of examples to process
        problem_types: List of problem types to process
        max_iterations: Maximum iterations for solution improvement
        output_dir: Directory for output files
    """
    # Check environment variables
    if model_type == "openai" and not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    if model_type == "claude" and not os.environ.get("ANTHROPIC_API_KEY"):
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    cyber_url = os.environ.get("CYBER_URL")
    if not cyber_url:
        raise ValueError("CYBER_URL environment variable is not set")

    # Set default model name if not provided
    if model_name is None:
        if model_type == "openai":
            model_name = "o3-mini"
        else:
            model_name = "claude-3-haiku-20240307"

    print(f"Step 1: Generating solutions using {model_name}...")

    # Use solution process for generation (set max_iterations=1 for generation only)
    generation_result: BatchResult = await solution_process(
        model_type=model_type,
        model_name=model_name,
        sample_size=sample_size,
        concurrency=5,
        problem_types=problem_types,
        output_dir=output_dir,
        cyber_url=cyber_url,
        max_iterations=1,  # Just generate solutions
    )

    # Process each problem type
    for problem_type in problem_types:
        # Use the solution file from the generation result
        solution_file = generation_result.generated_files.get(problem_type)
        if not solution_file:
            raise ValueError(f"No solution file found for problem type: {problem_type}")

        print(f"\nStep 2: Evaluating {problem_type} solutions...")
        evaluation_results = await evaluate_solutions_async(
            solution_file=solution_file, output_dir=output_dir
        )

        print(
            f"\nStep 3: Checking if improvement is needed for {problem_type} solutions..."
        )

        # Use the evaluation results directly instead of loading from file
        execution_results = [r.model_dump() for r in evaluation_results.results]

        # Count how many solutions already pass all tests
        all_tests_pass = all(
            result.get("model_tests_passed", 0) == result.get("model_tests_total", 0)
            for result in execution_results
        )

        if all_tests_pass:
            print(
                f"All {problem_type} solutions already pass all tests. Skipping improvement step."
            )
            # Use original solutions as "improved" solutions for comparison
            improved_file = solution_file
        else:
            print(f"Improving {problem_type} solutions...")

            # Use solution process for improvement
            improved_result = await solution_process(
                model_type=model_type,
                model_name=model_name,
                problem_types=[problem_type],
                cyber_url=cyber_url,
                max_iterations=max_iterations,
                target_passed_ratio=1.0,
                input_solution_file=solution_file,
                concurrency=3,
            )

            # Get the improved solution file
            improved_file = improved_result.generated_files.get(problem_type)
            if not improved_file:
                print(f"Warning: No improved solution file found for {problem_type}")
                improved_file = solution_file

        print(f"\nStep 4: Comparing original and improved {problem_type} solutions...")
        results = compare_solutions(
            original_file=solution_file,
            improved_file=improved_file,
            output_dir=output_dir,
        )

        # Print human-readable comparison
        print_comparison_results(results)

    print("\nWorkflow complete!")


def main():
    """Parse command line arguments and run the workflow."""
    parser = argparse.ArgumentParser(description="Run the LibraryBench workflow")
    parser.add_argument(
        "--model-type",
        choices=["openai", "claude"],
        default="claude",
        help="Type of model to use (openai or claude)",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        help="Specific model name (e.g., 'o3-mini' or 'claude-3-opus-20240229')",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=3,
        help="Number of examples to process for each problem type",
    )
    parser.add_argument(
        "--problem-types",
        nargs="+",
        choices=["search", "datastructure", "chess"],
        default=["chess"],
        help="Problem types to process",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Maximum number of improvement iterations per problem",
    )
    parser.add_argument(
        "--output-dir", type=str, default="data", help="Directory for output files"
    )

    args = parser.parse_args()

    asyncio.run(
        run_workflow(
            model_type=args.model_type,
            model_name=args.model_name,
            sample_size=args.sample_size,
            problem_types=args.problem_types,
            max_iterations=args.max_iterations,
            output_dir=args.output_dir,
        )
    )


if __name__ == "__main__":
    main()
