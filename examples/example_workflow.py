"""Example workflow demonstrating the full LibraryBench pipeline."""

import os
import asyncio
import argparse
from typing import Optional

from librarybench.generation import generate_solutions
from librarybench.execution import evaluate_solutions_async
from librarybench.improvement import batch_improve_solutions
from librarybench.analysis import compare_solutions, print_comparison_results


async def run_workflow(
    model_type: str = "claude",
    model_name: Optional[str] = None,
    sample_size: int = 5,
    problem_types: list = ["search"],
    max_iterations: int = 3,
    output_dir: str = "data",
):
    """Run the full LibraryBench workflow.

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
            model_name = "claude-3-7-sonnet-20250219"

    # Standardize model name for filenames
    model_key = model_name.replace("-", "_").replace(".", "_")

    print(f"Step 1: Generating solutions using {model_name}...")
    await generate_solutions(
        model_type=model_type,
        model_name=model_name,
        sample_size=sample_size,
        concurrency=5,
        problem_types=problem_types,
        output_dir=output_dir,
    )

    # Process each problem type
    for problem_type in problem_types:
        solution_file = f"{output_dir}/{model_key}_{problem_type}_solutions.json"

        print(f"\nStep 2: Evaluating {problem_type} solutions...")
        await evaluate_solutions_async(
            solution_file=solution_file, output_dir=output_dir
        )

        print(f"\nStep 3: Improving {problem_type} solutions...")
        improved_file = (
            f"{output_dir}/improved_{model_key}_{problem_type}_solutions.json"
        )
        await batch_improve_solutions(
            solution_file=solution_file,
            cyber_url=cyber_url,
            model_name=model_name,
            max_iterations=max_iterations,
            target_passed_ratio=1.0,
            output_file=improved_file,
            concurrent_problems=3,
        )

        print(f"\nStep 4: Comparing original and improved {problem_type} solutions...")
        model_solution_key = f"{model_key}_solution"
        results = compare_solutions(
            original_file=solution_file,
            improved_file=improved_file,
            model_key=model_solution_key,
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
