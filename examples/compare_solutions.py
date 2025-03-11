"""Compare original and improved solutions from LibraryBench."""

import os
import asyncio
import argparse
from typing import Optional

from librarybench.analysis.model_comparison import compare_solutions, print_comparison_results


def compare_model_solutions(
    original_file: str,
    improved_file: str,
    problem_id: Optional[int] = None,
    output_dir: str = "data",
):
    """
    Compare original and improved solutions.

    Args:
        original_file: Path to the original solution file
        improved_file: Path to the improved solution file
        model_key: Key to identify the model solutions
        problem_id: Optional ID of a specific problem to compare
        output_dir: Directory for output files
    """
    print(f"Comparing solutions from:")
    print(f"  Original: {original_file}")
    print(f"  Improved: {improved_file}")
    print()

    results = compare_solutions(
        original_file=original_file,
        improved_file=improved_file,
        problem_id=problem_id,
        output_dir=output_dir,
    )

    # Print human-readable comparison
    print_comparison_results(results)
    return results


def main():
    """Parse command line arguments and run the comparison."""
    parser = argparse.ArgumentParser(description="Compare model solution improvements")
    
    # Required arguments
    parser.add_argument(
        "--original-file", 
        type=str, 
        required=True,
        help="Path to the original solution file"
    )
    parser.add_argument(
        "--improved-file", 
        type=str, 
        required=True,
        help="Path to the improved solution file"
    )
    
    # Optional arguments
    parser.add_argument(
        "--problem-id",
        type=int,
        help="ID of a specific problem to compare (default: compare all)"
    )
    parser.add_argument(
        "--output-dir", 
        type=str, 
        default="data", 
        help="Directory for output files (default: data)"
    )

    args = parser.parse_args()

    compare_model_solutions(
        original_file=args.original_file,
        improved_file=args.improved_file,
        problem_id=args.problem_id,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
