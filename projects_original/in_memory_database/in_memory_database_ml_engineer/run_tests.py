#!/usr/bin/env python3
"""
Test runner for VectorDB.

This script runs all tests and generates the pytest_results.json file required for project completion.
"""

import os
import sys
import subprocess
import json


def run_tests():
    """Run all tests and generate pytest_results.json."""
    print("Running VectorDB tests...")
    
    # Make sure pytest-json-report is installed
    try:
        subprocess.run(
            ["pip", "install", "pytest-json-report"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        print(f"Error installing pytest-json-report: {e}")
        sys.exit(1)
    
    # Run the tests
    try:
        result = subprocess.run(
            [
                "pytest",
                "--json-report",
                "--json-report-file=pytest_results.json",
                "-v",
                "tests/"
            ],
            check=False,  # Don't exit on test failures, we'll check the result ourselves
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Print the output
        print(result.stdout.decode())
        if result.stderr:
            print(result.stderr.decode())
        
        # Check if the results file was created
        if not os.path.exists("pytest_results.json"):
            print("Error: pytest_results.json was not created.")
            sys.exit(1)
        
        # Load and analyze the results
        with open("pytest_results.json", "r") as f:
            results = json.load(f)
        
        # Print a summary
        summary = results.get("summary", {})
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        skipped = summary.get("skipped", 0)
        total = summary.get("total", 0)
        
        print(f"\nTest Summary:")
        print(f"  Total: {total}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Skipped: {skipped}")
        
        # Exit with an error code if any tests failed
        if failed > 0:
            print(f"\nError: {failed} tests failed.")
            sys.exit(1)
        else:
            print("\nSuccess! All tests passed.")
            
    except subprocess.CalledProcessError as e:
        print(f"Error running tests: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_tests()