# PyPatternGuard - Security Vulnerability Detection Engine

PyPatternGuard is a specialized code pattern detection system designed for cybersecurity specialists conducting security audits in fintech environments. It provides automated detection of security anti-patterns, vulnerability identification, and compliance reporting to ensure adherence to financial industry regulations.

## Features

- **OWASP Top 10 Vulnerability Detection**: Comprehensive detection of critical web application security risks
- **Cryptographic Misuse Detection**: Identifies weak algorithms, hardcoded secrets, and improper cryptographic implementations
- **Input Validation Analysis**: Detects SQL injection, XSS, and other input-related vulnerabilities
- **Compliance Reporting**: Automated mapping to PCI-DSS and SOC2 requirements
- **False Positive Suppression**: Intelligent suppression with full audit trail
- **Multiple Export Formats**: JSON and XML report generation for integration with other tools

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd pypatternguard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Usage

### Basic Scanning

```python
from pypatternguard import SecurityScanner

# Create scanner instance
scanner = SecurityScanner()

# Scan a project directory
scan_result = scanner.scan("/path/to/project")

# Print summary
stats = scan_result.get_summary_stats()
print(f"Found {stats['total_vulnerabilities']} vulnerabilities")
print(f"Critical: {stats['severity_distribution']['critical']}")
print(f"High: {stats['severity_distribution']['high']}")
```

### Advanced Configuration

```python
from pypatternguard import SecurityScanner, ScannerConfig

# Configure scanner
config = ScannerConfig(
    max_workers=4,
    min_confidence_threshold=0.8,
    file_extensions=[".py", ".pyw"],
    exclude_patterns=["__pycache__", ".git", "venv"],
    suppression_file="/path/to/suppressions.json"
)

scanner = SecurityScanner(config)
```

### Generating Compliance Reports

```python
# Generate compliance report
compliance_report = scanner.generate_compliance_report(scan_result)

# Check compliance scores
print(f"PCI-DSS Score: {compliance_report.compliance_scores['PCI-DSS']}%")
print(f"SOC2 Score: {compliance_report.compliance_scores['SOC2']}%")

# Export reports
scanner.export_results(scan_result, "scan_results.json", "json")
scanner.export_results(scan_result, "scan_results.xml", "xml")
```

### Managing False Positives

```python
from pypatternguard.suppression import SuppressionManager
from pypatternguard.models import SuppressionRule

# Create suppression manager
suppression_manager = SuppressionManager()

# Add suppression rule
rule = SuppressionRule(
    id="suppress-test-files",
    pattern="tests/.*",
    reason="Test files contain intentional vulnerabilities",
    created_by="security_team",
    created_at=datetime.now()
)
suppression_manager.add_rule(rule)

# Save rules
suppression_manager.save_rules("suppressions.json")
```

## Vulnerability Types Detected

### OWASP Top 10
- **Injection (A03)**: SQL injection, command injection, code injection
- **Broken Authentication (A07)**: Weak password hashing, hardcoded credentials
- **Sensitive Data Exposure (A02)**: Hardcoded secrets, weak encryption
- **XML External Entities (A05)**: XXE vulnerabilities
- **Broken Access Control (A01)**: Authorization flaws
- **Security Misconfiguration (A05)**: Insecure defaults
- **Cross-Site Scripting (A03)**: XSS vulnerabilities
- **Insecure Deserialization (A08)**: Unsafe pickle/yaml usage
- **Using Components with Known Vulnerabilities (A06)**: Outdated dependencies
- **Insufficient Logging & Monitoring (A09)**: Missing security logging

### Cryptographic Issues
- Weak hashing algorithms (MD5, SHA1)
- Weak encryption ciphers (DES, 3DES, RC4)
- Insecure cipher modes (ECB)
- Hardcoded encryption keys and IVs
- Predictable random number generation

### Input Validation
- SQL injection via string concatenation
- Command injection through os.system/subprocess
- Code injection via eval/exec
- Path traversal vulnerabilities
- Cross-site scripting (XSS)

## Compliance Mapping

PyPatternGuard automatically maps detected vulnerabilities to compliance requirements:

### PCI-DSS
- Requirement 2.3: Encrypt non-console administrative access
- Requirement 3.4: Render PAN unreadable anywhere stored
- Requirement 6.5.1: Injection flaws
- Requirement 6.5.7: Cross-site scripting
- Requirement 8.2.1: Strong authentication credentials

### SOC2
- CC6.1: Logical and physical access controls
- CC6.7: Transmission and disclosure of information
- CC7.1: System operations
- CC7.2: System monitoring

## Running Tests

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=pypatternguard

# Generate JSON test report (REQUIRED)
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

## Performance

PyPatternGuard is designed for high performance:
- Scans 100,000 lines of code in under 5 minutes
- Memory usage under 2GB for typical codebases
- Supports parallel processing with configurable workers
- Incremental scanning for faster re-analysis

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| max_file_size_mb | 10.0 | Maximum file size to scan |
| max_workers | 4 | Number of parallel workers |
| min_confidence_threshold | 0.7 | Minimum confidence for reporting |
| file_extensions | [".py", ".pyw"] | File types to scan |
| exclude_patterns | ["__pycache__", ".git", "venv"] | Patterns to exclude |

## Output Formats

### JSON Report Structure
```json
{
  "scan_id": "uuid",
  "timestamp": "2024-01-15T10:30:00",
  "total_files_scanned": 25,
  "vulnerabilities": [
    {
      "id": "SQLI-001",
      "type": "injection",
      "severity": "critical",
      "title": "SQL Injection",
      "location": {
        "file_path": "/app/db.py",
        "line_start": 42
      },
      "remediation": "Use parameterized queries",
      "compliance_mappings": {
        "PCI-DSS": ["6.5.1"],
        "SOC2": ["CC6.1"]
      }
    }
  ]
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests to ensure everything passes
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on the GitHub repository.