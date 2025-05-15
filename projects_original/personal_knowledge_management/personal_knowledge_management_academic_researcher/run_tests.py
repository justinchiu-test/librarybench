#!/usr/bin/env python
"""
Script to run tests and generate pytest_results.json.
"""

import os
import subprocess
import sys

def main():
    """Run tests and generate pytest_results.json."""
    # Install pytest-json-report if needed
    try:
        subprocess.run(
            ["uv", "pip", "install", "pytest-json-report"],
            check=True
        )
    except subprocess.CalledProcessError:
        print("Failed to install pytest-json-report")
        return 1

    # Run all tests excluding the performance tests
    try:
        subprocess.run(
            [
                "uv", "run", "pytest",
                "tests/citations/test_formatters.py",
                "tests/citations/test_parsers.py",
                "tests/core/test_models.py",
                "tests/core/test_storage.py",
                "tests/core/test_brain.py",
                "tests/experiments/test_templates.py",
                "tests/grants/test_export.py",
                "tests/test_bidirectional_linking.py",
                "tests/test_citation_accuracy.py",
                "tests/test_collaboration.py",
                "tests/test_experiment_templates.py",
                "tests/test_grant_proposals.py",
                "tests/test_research_questions.py",
                "tests/test_workflows.py",
                "--json-report",
                "--json-report-file=pytest_results.json",
                "-o", "addopts="
            ],
            check=True
        )

        print("Tests completed successfully. Results saved to pytest_results.json")

        return 0
    except subprocess.CalledProcessError:
        print("Tests failed. Check pytest_results.json for details")
        return 1

if __name__ == "__main__":
    sys.exit(main())