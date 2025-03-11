"""Model comparison module for analyzing improvements."""

import os
import json
from typing import Dict, Any, Optional

from librarybench.types import SolutionResult


def compare_solutions(
    original_file: str,
    improved_file: str,
    problem_id: Optional[int] = None,
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compare original and improved solutions.

    Args:
        original_file: Path to the original solution file
        improved_file: Path to the improved solution file
        problem_id: Optional ID of a specific problem to compare (if None, compare all)
        output_dir: Directory for output files (defaults to "data")

    Returns:
        Dictionary with comparison results
    """
    # Set default output directory
    if output_dir is None:
        output_dir = "data"

    # Ensure original_file has correct path prefix if needed
    if not os.path.dirname(original_file):
        original_file = os.path.join(output_dir, original_file)

    # Ensure improved_file has correct path prefix if needed
    if not os.path.dirname(improved_file):
        improved_file = os.path.join(output_dir, improved_file)

    # Load original solutions
    with open(original_file, "r") as f:
        original_solutions = json.load(f)

    # Load improved solutions
    with open(improved_file, "r") as f:
        improved_solutions = json.load(f)

    original_solutions = [SolutionResult.model_validate(x) for x in original_solutions]
    improved_solutions = [SolutionResult.model_validate(x) for x in improved_solutions]

    # Track improvement statistics
    results = {
        "total_problems": 0,
        "improved_problems": 0,
        "unchanged_problems": 0,
        "worse_problems": 0,
        "original_total_passed": 0,
        "original_total_tests": 0,
        "improved_total_passed": 0,
        "improved_total_tests": 0,
        "problem_details": [],
    }

    # Compare each problem
    for i, (orig_solution, imp_solution) in enumerate(
        zip(original_solutions, improved_solutions)
    ):
        # Update statistics
        results["total_problems"] += 1
        results["original_total_passed"] += orig_solution.tests_passed
        results["original_total_tests"] += orig_solution.tests_total
        results["improved_total_passed"] += imp_solution.tests_passed
        results["improved_total_tests"] += imp_solution.tests_total

        # Determine if improved
        if imp_solution.pass_ratio > orig_solution.pass_ratio:
            status = "improved"
            results["improved_problems"] += 1
        elif imp_solution.pass_ratio == orig_solution.pass_ratio:
            status = "unchanged"
            results["unchanged_problems"] += 1
        else:
            status = "worse"
            results["worse_problems"] += 1

        # Add problem detail
        results["problem_details"].append(
            {
                "problem_id": orig_solution.problem.problem_id,
                "status": status,
                "original_passed": orig_solution.tests_passed,
                "original_total": orig_solution.tests_total,
                "original_ratio": orig_solution.pass_ratio,
                "improved_passed": imp_solution.tests_passed,
                "improved_total": imp_solution.tests_total,
                "improved_ratio": imp_solution.pass_ratio,
                "improvement": imp_solution.pass_ratio - orig_solution.pass_ratio,
            }
        )

    # Calculate overall ratios
    results["original_overall_ratio"] = (
        results["original_total_passed"] / results["original_total_tests"]
        if results["original_total_tests"] > 0
        else 0
    )
    results["improved_overall_ratio"] = (
        results["improved_total_passed"] / results["improved_total_tests"]
        if results["improved_total_tests"] > 0
        else 0
    )
    results["overall_improvement"] = (
        results["improved_overall_ratio"] - results["original_overall_ratio"]
    )

    return results


def print_comparison_results(results: Dict[str, Any]) -> None:
    """Print comparison results in a human-readable format.

    Args:
        results: Dictionary with comparison results from compare_solutions
    """
    print("=" * 50)
    print("SOLUTION IMPROVEMENT COMPARISON")
    print("=" * 50)

    print(f"Total problems evaluated: {results['total_problems']}")

    # Only calculate percentages if there are problems
    if results["total_problems"] > 0:
        print(
            f"Problems improved: {results['improved_problems']} ({results['improved_problems'] / results['total_problems'] * 100:.1f}%)"
        )
        print(
            f"Problems unchanged: {results['unchanged_problems']} ({results['unchanged_problems'] / results['total_problems'] * 100:.1f}%)"
        )
        print(
            f"Problems worse: {results['worse_problems']} ({results['worse_problems'] / results['total_problems'] * 100:.1f}%)"
        )
    else:
        print("Problems improved: 0 (0.0%)")
        print("Problems unchanged: 0 (0.0%)")
        print("Problems worse: 0 (0.0%)")

    print("\nTest passing rates:")
    print(
        f"Original solutions: {results['original_total_passed']}/{results['original_total_tests']} ({results['original_overall_ratio'] * 100:.1f}%)"
    )
    print(
        f"Improved solutions: {results['improved_total_passed']}/{results['improved_total_tests']} ({results['improved_overall_ratio'] * 100:.1f}%)"
    )
    print(f"Overall improvement: {results['overall_improvement'] * 100:.1f}%")

    # Only show most improved problems if there are any problems
    if results["problem_details"]:
        print("\nTop 5 most improved problems:")
        most_improved = sorted(
            results["problem_details"], key=lambda x: x["improvement"], reverse=True
        )[:5]
        for i, prob in enumerate(most_improved, 1):
            print(
                f"{i}. Problem {prob['problem_id']}: {prob['original_passed']}/{prob['original_total']} ({prob['original_ratio'] * 100:.1f}%) -> {prob['improved_passed']}/{prob['improved_total']} ({prob['improved_ratio'] * 100:.1f}%) [{prob['improvement'] * 100:.1f}% improvement]"
            )
    else:
        print("\nNo problems to show improvement stats for.")

    if results["worse_problems"] > 0:
        print("\nProblems that got worse:")
        worse = [p for p in results["problem_details"] if p["status"] == "worse"]
        for i, prob in enumerate(worse, 1):
            print(
                f"{i}. Problem {prob['problem_id']}: {prob['original_passed']}/{prob['original_total']} ({prob['original_ratio'] * 100:.1f}%) -> {prob['improved_passed']}/{prob['improved_total']} ({prob['improved_ratio'] * 100:.1f}%) [{-prob['improvement'] * 100:.1f}% decline]"
            )

    print("=" * 50)


def save_comparison_results(
    results: Dict[str, Any], output_file: str, output_dir: Optional[str] = None
) -> str:
    """Save comparison results to a JSON file.

    Args:
        results: Dictionary with comparison results
        output_file: Name of the output file
        output_dir: Directory for output files (defaults to "data")

    Returns:
        Path to the saved file
    """
    # Set default output directory
    if output_dir is None:
        output_dir = "data"

    # Ensure output file goes to correct directory
    if not os.path.dirname(output_file):
        output_file = os.path.join(output_dir, output_file)

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    return output_file
