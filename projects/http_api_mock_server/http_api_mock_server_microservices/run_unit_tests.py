#!/usr/bin/env python
"""Run unit tests in batches to avoid timeout."""

import subprocess
import sys
import json

test_modules = [
    "tests/test_models.py",
    "tests/test_service_registry.py", 
    "tests/test_dependency_manager.py",
    "tests/test_circuit_breaker.py",
    "tests/test_tracing.py",
    "tests/test_chaos_controller.py"
]

all_passed = True
for module in test_modules:
    print(f"\nRunning {module}...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", module, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        all_passed = False

# Now run all tests with JSON report
print("\nGenerating JSON report...")
result = subprocess.run([
    sys.executable, "-m", "pytest",
    *test_modules,
    "--json-report",
    "--json-report-file=pytest_results.json",
    "-q"
], capture_output=True, text=True)

print(result.stdout)
if result.returncode != 0:
    print(result.stderr)

# Check test count
try:
    with open("pytest_results.json", "r") as f:
        report = json.load(f)
        total_tests = report["summary"]["total"]
        print(f"\nTotal tests: {total_tests}")
        if total_tests < 100:
            print(f"WARNING: Only {total_tests} tests found, need at least 100")
except Exception as e:
    print(f"Error reading report: {e}")

sys.exit(0 if all_passed else 1)