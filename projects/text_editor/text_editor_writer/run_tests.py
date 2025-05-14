#!/usr/bin/env python
"""Run tests and generate the pytest_results.json file."""

import os
import sys
import subprocess
import json
from pathlib import Path


def main():
    """Run tests and generate the pytest_results.json file."""
    # Ensure we're in the project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Make sure we have pytest-json-report
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pytest-json-report"],
            check=True
        )
        print("pytest-json-report installed successfully.")
    except subprocess.CalledProcessError:
        print("Failed to install pytest-json-report.")
        return 1
    
    # Run the tests with json report
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                "--json-report",
                "--json-report-file=pytest_results.json"
            ],
            capture_output=True,
            text=True,
            check=False  # Don't raise exception on test failure
        )
        
        print(result.stdout)
        
        # Check if we have the json report
        json_report_path = project_root / "pytest_results.json"
        if json_report_path.exists():
            # Load and check the report
            with open(json_report_path, "r") as f:
                report = json.load(f)
            
            print("\nTest Summary:")
            print(f"Total tests: {report['summary']['total']}")
            print(f"Passed: {report['summary']['passed']}")
            print(f"Failed: {report['summary']['failed']}")
            print(f"Skipped: {report['summary']['skipped']}")
            print(f"Errors: {report['summary']['errors']}")
            print(f"Duration: {report['duration']:.2f} seconds")
            
            # Return exit code based on test results
            return 0 if report['summary']['failed'] == 0 and report['summary']['errors'] == 0 else 1
        else:
            print("Failed to generate pytest_results.json")
            return 1
        
    except subprocess.CalledProcessError as e:
        print(f"Error running tests: {e}")
        print(e.stdout)
        print(e.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())