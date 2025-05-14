# Compliance Data Discovery Analyzer

A specialized file system analyzer focused on identifying sensitive information and ensuring regulatory compliance.

## Overview

The Compliance Data Discovery Analyzer is a Python library designed to help information security specialists conduct thorough audits for regulatory compliance. It provides tools for pattern-based scanning to detect sensitive information, comprehensive audit logging, customizable compliance reporting, differential scanning to identify changes, and chain-of-custody tracking to ensure the integrity of findings.

## Core Features

1. **Sensitive Data Detection Engine**: Pattern matching for PII and sensitive data
2. **Audit Integrity Framework**: Immutable, detailed logging for compliance evidence
3. **Regulatory Compliance Reporting**: Reports mapped to GDPR, HIPAA, SOX, etc.
4. **Differential Scanning**: Identify newly added sensitive content since previous audits
5. **Chain-of-Custody Tracking**: Cryptographic verification for evidence integrity

## Installation

```bash
pip install -e .
```

## Usage

```python
from file_system_analyzer.scanner import ComplianceScanner
from file_system_analyzer.rules import PredefinedRules

# Create a scanner with predefined rules
scanner = ComplianceScanner(rules=PredefinedRules.GDPR)

# Scan a directory
results = scanner.scan_directory("/path/to/data")

# Generate a compliance report
report = results.generate_report("GDPR")

# Save the report with cryptographic verification
report.save("/path/to/output", verify=True)
```

## Development

This project uses:
- Pytest for testing
- Ruff for formatting and linting
- Pyright for type checking

To set up the development environment:

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install the project in development mode
uv pip install -e .

# Install development dependencies
uv pip install pytest pytest-cov pytest-json-report ruff pyright

# Run tests
pytest --json-report --json-report-file=pytest_results.json
```