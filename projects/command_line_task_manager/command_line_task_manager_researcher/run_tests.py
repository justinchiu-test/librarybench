#!/usr/bin/env python
"""
Script to run the test suite and generate a JSON report.

This script runs pytest with configurations to generate a detailed JSON report
of test results, which can be used for analysis or documentation.
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run the test suite and generate a JSON report."
    )
    parser.add_argument(
        "--output", "-o",
        default="report.json",
        help="Path to the output JSON report file (default: report.json)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose test output"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--performance", "-p",
        action="store_true",
        help="Run performance tests only"
    )
    parser.add_argument(
        "--unit", "-u",
        action="store_true",
        help="Run unit tests only"
    )
    parser.add_argument(
        "--integration", "-i",
        action="store_true",
        help="Run integration tests only"
    )
    return parser.parse_args()


def run_tests(args):
    """Run pytest with the specified arguments."""
    pytest_args = ["pytest"]
    
    # Add verbosity option
    if args.verbose:
        pytest_args.append("-v")
    
    # Configure test selection
    if args.unit:
        # Exclude performance and integration tests
        pytest_args.extend([
            "tests/task_management",
            "tests/bibliography",
            "tests/dataset_versioning",
            "tests/environment",
            "tests/export",
            "tests/experiment_tracking"
        ])
    elif args.integration:
        pytest_args.append("tests/integration")
    elif args.performance:
        pytest_args.append("tests/performance")
    
    # Configure coverage
    if args.coverage:
        pytest_args.extend([
            "--cov=researchtrack",
            "--cov-report=term",
            "--cov-report=html:coverage_report"
        ])
    
    # Configure JSON report
    pytest_args.extend([
        "--json-report",
        f"--json-report-file={args.output}"
    ])
    
    # Print the command being run
    command = " ".join(pytest_args)
    print(f"Running: {command}")
    
    # Run the tests
    result = subprocess.run(pytest_args, capture_output=args.verbose)
    
    # Return the exit code
    return result.returncode


def analyze_report(report_path):
    """Analyze the JSON report and print summary information."""
    if not os.path.exists(report_path):
        print(f"Error: Report file {report_path} not found.")
        return False
    
    try:
        with open(report_path, "r") as f:
            report = json.load(f)
        
        summary = report.get("summary", {})
        test_count = summary.get("total", 0)
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        skipped = summary.get("skipped", 0)
        errors = summary.get("error", 0)
        duration = summary.get("duration", 0)
        
        # Create a formatted summary
        print("\n==================================")
        print("  TEST EXECUTION SUMMARY")
        print("==================================")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Tests: {test_count}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Skipped: {skipped}")
        print(f"Errors: {errors}")
        print(f"Success Rate: {passed / test_count * 100:.2f}%" if test_count > 0 else "Success Rate: N/A")
        print(f"Total Duration: {duration:.2f} seconds")
        print("==================================\n")
        
        # If there are failures, print them
        if failed > 0 or errors > 0:
            print("FAILED TESTS:")
            tests = report.get("tests", [])
            for test in tests:
                if test.get("outcome") == "failed":
                    print(f"  - {test.get('nodeid')}")
                    print(f"    Reason: {test.get('call', {}).get('longrepr', 'No details available')}")
                    print()
        
        return True
    
    except Exception as e:
        print(f"Error analyzing report: {e}")
        return False


def main():
    """Main function to run tests and analyze results."""
    args = parse_args()
    
    # Run the tests
    exit_code = run_tests(args)
    
    # Analyze the report if it was generated
    if os.path.exists(args.output):
        analyze_report(args.output)
    
    # Return the pytest exit code
    return exit_code


if __name__ == "__main__":
    sys.exit(main())