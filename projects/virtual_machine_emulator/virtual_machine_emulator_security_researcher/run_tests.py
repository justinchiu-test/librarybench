"""
Script to run the test suite for the secure VM emulator.
"""

import os
import sys
import subprocess

def main():
    """Run the test suite."""
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Run pytest
    cmd = [
        "pytest",
        "--json-report",
        "--json-report-file=pytest_results.json",
        "-v"
    ]
    
    process = subprocess.Popen(
        cmd,
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    # Stream the output to the console
    for line in process.stdout:
        print(line, end="")
    
    # Wait for the process to finish
    process.wait()
    
    # Check if the report was generated
    report_path = os.path.join(project_root, "pytest_results.json")
    if os.path.exists(report_path):
        print(f"\nTest report generated: {report_path}")
    else:
        print("\nFailed to generate test report.")
    
    return process.returncode

if __name__ == "__main__":
    sys.exit(main())