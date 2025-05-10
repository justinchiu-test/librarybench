#!/usr/bin/env python
"""Script to run all tests for the MobileSyncDB project."""

import os
import sys
import subprocess
import argparse
import time


def run_command(command, title=None, timeout=None):
    """Run a command and print output."""
    if title:
        print(f"\n=== {title} ===\n")
    
    start_time = time.time()
    result = subprocess.run(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout,
    )
    
    print(result.stdout)
    
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        return False
    
    duration = time.time() - start_time
    print(f"Completed in {duration:.2f} seconds")
    return True


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run MobileSyncDB tests")
    parser.add_argument(
        "--unit", action="store_true", 
        help="Run unit tests only"
    )
    parser.add_argument(
        "--performance", action="store_true", 
        help="Run performance tests only"
    )
    parser.add_argument(
        "--examples", action="store_true", 
        help="Run examples only"
    )
    parser.add_argument(
        "--all", action="store_true", 
        help="Run all tests and examples"
    )
    parser.add_argument(
        "--lint", action="store_true", 
        help="Run linting (ruff check)"
    )
    parser.add_argument(
        "--typecheck", action="store_true", 
        help="Run type checking (pyright)"
    )
    parser.add_argument(
        "--format", action="store_true", 
        help="Run code formatting (ruff format)"
    )
    
    args = parser.parse_args()
    
    # If no specific tests are requested, run all
    if not (args.unit or args.performance or args.examples or args.all or 
            args.lint or args.typecheck or args.format):
        args.all = True
    
    return args


def main():
    """Run specified tests."""
    args = parse_args()
    success = True
    
    # Determine which tests to run
    run_all = args.all
    run_unit = args.unit or run_all
    run_performance = args.performance or run_all
    run_examples = args.examples or run_all
    run_lint = args.lint or run_all
    run_typecheck = args.typecheck or run_all
    run_format = args.format
    
    # Run type checking
    if run_typecheck:
        success = run_command(
            "uv run pyright",
            "Type Checking (pyright)"
        ) and success
    
    # Run linting
    if run_lint:
        success = run_command(
            "uv run ruff check .",
            "Linting (ruff check)"
        ) and success
    
    # Run formatting
    if run_format:
        success = run_command(
            "uv run ruff format .",
            "Formatting (ruff format)"
        ) and success
    
    # Run unit tests
    if run_unit:
        success = run_command(
            "uv run pytest tests/unit -v",
            "Unit Tests"
        ) and success
    
    # Run performance tests
    if run_performance:
        success = run_command(
            "uv run pytest tests/performance -v",
            "Performance Tests"
        ) and success
    
    # Run examples
    if run_examples:
        # Basic usage example
        success = run_command(
            "uv run python examples/basic_usage.py",
            "Running Basic Usage Example",
            timeout=60
        ) and success
        
        # Conflict resolution example
        success = run_command(
            "uv run python examples/conflict_resolution.py",
            "Running Conflict Resolution Example",
            timeout=60
        ) and success
    
    # Print summary
    print("\n=== Test Summary ===\n")
    if success:
        print("All tests completed successfully!")
    else:
        print("Some tests failed. See output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()