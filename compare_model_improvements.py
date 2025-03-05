import os
import json
import argparse
from typing import Dict, Any, List, Tuple

from model_feedback import (
    extract_code,
    run_unit_tests,
    create_test_cases_from_input_output,
)


def evaluate_solution(
    code: str, stdin_stdout_tests: List[Dict[str, str]]
) -> Tuple[int, int, float]:
    """
    Evaluate a solution against test cases
    
    Returns:
        Tuple of (passed tests, total tests, pass ratio)
    """
    # Run code against test cases
    test_results = run_unit_tests([code], stdin_stdout_tests)
    test_results_flat = test_results[0] if test_results else []
    
    # Calculate pass rate
    passed = sum(1 for result in test_results_flat if result.get("passed", False))
    total = len(stdin_stdout_tests)
    passed_ratio = passed / total if total > 0 else 0
    
    return passed, total, passed_ratio


def compare_solutions(
    original_file: str,
    improved_file: str,
    model_key: str = "claude_solution",
    problem_id: int = None,
) -> Dict[str, Any]:
    """
    Compare original and improved solutions
    
    Args:
        original_file: Path to the original solution file
        improved_file: Path to the improved solution file
        model_key: Key to identify the model solutions (e.g., 'claude_solution', 'o3_mini_solution')
        problem_id: Optional ID of a specific problem to compare (if None, compare all)
        
    Returns:
        Dictionary with comparison results
    """
    # Ensure original_file has data/ prefix if it doesn't already
    if not original_file.startswith("data/") and not os.path.dirname(original_file):
        original_file = os.path.join("data", original_file)
    
    # Ensure improved_file has data/ prefix if it doesn't already
    if not improved_file.startswith("data/") and not os.path.dirname(improved_file):
        improved_file = os.path.join("data", improved_file)
    
    # Load original solutions
    with open(original_file, "r") as f:
        original_solutions = json.load(f)
    
    # Load improved solutions
    with open(improved_file, "r") as f:
        improved_solutions = json.load(f)
    
    # Filter to specific problem if requested
    if problem_id is not None:
        original_solutions = [original_solutions[problem_id]]
        improved_solutions = [improved_solutions[problem_id]]
    
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
        "problem_details": []
    }
    
    # Compare each problem
    for i, (orig_solution, imp_solution) in enumerate(zip(original_solutions, improved_solutions)):
        # Skip if no improved solution
        improved_key = f"improved_{model_key}"
        if improved_key not in imp_solution:
            continue
        
        # Extract the original and improved code
        original_code = extract_code(orig_solution.get(model_key, ""))
        improved_code = extract_code(imp_solution.get(improved_key, ""))
        
        # Get the input_output field
        input_output = orig_solution.get("input_output")
        if not input_output:
            continue
        
        # Parse input_output if it's a string
        if isinstance(input_output, str):
            try:
                input_output = json.loads(input_output)
            except json.JSONDecodeError:
                continue
        
        # Format as stdin/stdout tests
        stdin_stdout_tests = create_test_cases_from_input_output(input_output)
        if not stdin_stdout_tests:
            continue
        
        # Evaluate original solution
        orig_passed, orig_total, orig_ratio = evaluate_solution(original_code, stdin_stdout_tests)
        
        # Evaluate improved solution
        imp_passed, imp_total, imp_ratio = evaluate_solution(improved_code, stdin_stdout_tests)
        
        # Update statistics
        results["total_problems"] += 1
        results["original_total_passed"] += orig_passed
        results["original_total_tests"] += orig_total
        results["improved_total_passed"] += imp_passed
        results["improved_total_tests"] += imp_total
        
        # Determine if improved
        if imp_ratio > orig_ratio:
            status = "improved"
            results["improved_problems"] += 1
        elif imp_ratio == orig_ratio:
            status = "unchanged"
            results["unchanged_problems"] += 1
        else:
            status = "worse"
            results["worse_problems"] += 1
        
        # Add problem detail
        results["problem_details"].append({
            "problem_id": i,
            "status": status,
            "original_passed": orig_passed,
            "original_total": orig_total,
            "original_ratio": orig_ratio,
            "improved_passed": imp_passed,
            "improved_total": imp_total,
            "improved_ratio": imp_ratio,
            "improvement": imp_ratio - orig_ratio
        })
    
    # Calculate overall ratios
    results["original_overall_ratio"] = (
        results["original_total_passed"] / results["original_total_tests"]
        if results["original_total_tests"] > 0 else 0
    )
    results["improved_overall_ratio"] = (
        results["improved_total_passed"] / results["improved_total_tests"]
        if results["improved_total_tests"] > 0 else 0
    )
    results["overall_improvement"] = results["improved_overall_ratio"] - results["original_overall_ratio"]
    
    return results


def print_comparison_results(results: Dict[str, Any]):
    """Print comparison results in a human-readable format"""
    print("=" * 50)
    print("SOLUTION IMPROVEMENT COMPARISON")
    print("=" * 50)
    
    print(f"Total problems evaluated: {results['total_problems']}")
    print(f"Problems improved: {results['improved_problems']} ({results['improved_problems']/results['total_problems']*100:.1f}%)")
    print(f"Problems unchanged: {results['unchanged_problems']} ({results['unchanged_problems']/results['total_problems']*100:.1f}%)")
    print(f"Problems worse: {results['worse_problems']} ({results['worse_problems']/results['total_problems']*100:.1f}%)")
    
    print("\nTest passing rates:")
    print(f"Original solutions: {results['original_total_passed']}/{results['original_total_tests']} ({results['original_overall_ratio']*100:.1f}%)")
    print(f"Improved solutions: {results['improved_total_passed']}/{results['improved_total_tests']} ({results['improved_overall_ratio']*100:.1f}%)")
    print(f"Overall improvement: {results['overall_improvement']*100:.1f}%")
    
    print("\nTop 5 most improved problems:")
    most_improved = sorted(results["problem_details"], key=lambda x: x["improvement"], reverse=True)[:5]
    for i, prob in enumerate(most_improved, 1):
        print(f"{i}. Problem {prob['problem_id']}: {prob['original_passed']}/{prob['original_total']} ({prob['original_ratio']*100:.1f}%) → {prob['improved_passed']}/{prob['improved_total']} ({prob['improved_ratio']*100:.1f}%) [{prob['improvement']*100:.1f}% improvement]")
    
    if results["worse_problems"] > 0:
        print("\nProblems that got worse:")
        worse = [p for p in results["problem_details"] if p["status"] == "worse"]
        for i, prob in enumerate(worse, 1):
            print(f"{i}. Problem {prob['problem_id']}: {prob['original_passed']}/{prob['original_total']} ({prob['original_ratio']*100:.1f}%) → {prob['improved_passed']}/{prob['improved_total']} ({prob['improved_ratio']*100:.1f}%) [{-prob['improvement']*100:.1f}% decline]")
    
    print("=" * 50)


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Compare original and improved model solutions")
    parser.add_argument("--original-file", type=str, required=True, help="Path to the original solution file")
    parser.add_argument("--improved-file", type=str, required=True, help="Path to the improved solution file")
    parser.add_argument("--model-key", type=str, default="claude_solution", help="Key for the model solutions")
    parser.add_argument("--problem-id", type=int, help="Optional ID of a specific problem to compare")
    parser.add_argument("--output-file", type=str, help="Optional file to save comparison results as JSON")
    args = parser.parse_args()
    
    # Compare solutions
    results = compare_solutions(
        original_file=args.original_file,
        improved_file=args.improved_file,
        model_key=args.model_key,
        problem_id=args.problem_id
    )
    
    # Print results
    print_comparison_results(results)
    
    # Save results if requested
    if args.output_file:
        # Ensure output file goes to data/ directory
        output_file = args.output_file
        if not output_file.startswith("data/") and not os.path.dirname(output_file):
            output_file = os.path.join("data", output_file)
        
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {output_file}")


if __name__ == "__main__":
    main()