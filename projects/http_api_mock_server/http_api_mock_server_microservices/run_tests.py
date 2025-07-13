#!/usr/bin/env python
"""Run tests and generate JSON report."""

import subprocess
import sys

# Run pytest with JSON report
result = subprocess.run([
    sys.executable, "-m", "pytest",
    "--json-report",
    "--json-report-file=pytest_results.json",
    "-v",
    "--tb=short",
    "-x"  # Stop on first failure
], capture_output=True, text=True)

print(result.stdout)
print(result.stderr)

sys.exit(result.returncode)