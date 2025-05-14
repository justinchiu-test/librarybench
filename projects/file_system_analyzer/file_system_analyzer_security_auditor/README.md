# Compliance Data Discovery Analyzer

A specialized file system analyzer focused on identifying sensitive information and ensuring regulatory compliance.

## Overview

The Compliance Data Discovery Analyzer is a Python library designed to help information security specialists conduct thorough audits for regulatory compliance. It provides tools for pattern-based scanning to detect sensitive information, comprehensive audit logging, customizable compliance reporting, differential scanning to identify changes, and chain-of-custody tracking to ensure the integrity of findings.

## Key Security and Compliance Features

1. **Pattern-Based Scanning for Sensitive Data**: Advanced algorithms detect PII and other sensitive data types across diverse file formats including personal identifiers, financial information, health records, and proprietary business data.

2. **Comprehensive Audit Logging**: Immutable, detailed logging of all scan operations with cryptographic verification, providing defensible evidence of what was scanned, when, by whom, and what was found.

3. **Customizable Compliance Reporting**: Reporting tools mapped to specific regulatory frameworks (GDPR, HIPAA, SOX, PCI-DSS) with appropriate categorization and contextual information for compliance requirements.

4. **Differential Scanning**: Efficient identification of newly added sensitive content since previous scans, allowing for targeted remediation without reviewing previously addressed issues.

5. **Chain-of-Custody Tracking**: Cryptographic verification systems for exported reports, ensuring evidence integrity with proof that reports haven't been modified since creation.

## Installation

```bash
# Install from the repository
pip install -e .

# OR install with all requirements
pip install -r requirements.txt
```

## Usage

```python
from file_system_analyzer.scanner import ComplianceScanner, ComplianceScanOptions
from file_system_analyzer.detection.patterns import ComplianceCategory, SensitivityLevel

# Configure scan options
options = ComplianceScanOptions(
    output_dir="/path/to/output",
    create_baseline=True,
    baseline_name="Initial Baseline",
    report_frameworks=["gdpr", "pci-dss"],
    create_evidence_package=True
)

# Create scanner
scanner = ComplianceScanner(options=options)

# Scan a directory
summary = scanner.scan_directory("/path/to/data")

# Print scan summary
print(f"Files scanned: {summary.total_files}")
print(f"Files with sensitive data: {summary.files_with_sensitive_data}")
print(f"Total sensitive data matches: {summary.total_matches}")
```

## Security Features

- **Tamper-evident logging**: Provides immutable and cryptographically verifiable audit logs
- **Cryptographic verification**: Ensures evidence integrity with digital signatures
- **Context-aware detection**: Minimizes false positives in sensitive data identification
- **Risk-level assessment**: Categorizes findings by severity and compliance impact
- **Chain-of-custody**: Maintains complete evidence trail with access logging

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

# Install the project in development mode with all dependencies
pip install -e .
pip install -r requirements.txt

# Run tests with JSON report
pytest --json-report --json-report-file=pytest_results.json
```