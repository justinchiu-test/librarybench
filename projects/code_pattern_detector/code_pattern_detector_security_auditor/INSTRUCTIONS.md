# PyPatternGuard - Security Vulnerability Detection Engine

## Overview
A specialized code pattern detection system designed for cybersecurity specialists conducting security audits in fintech environments. This implementation focuses on automated detection of security anti-patterns, vulnerability identification, and compliance reporting to ensure adherence to financial industry regulations.

## Persona Description
A cybersecurity specialist who conducts security audits for fintech companies and needs to quickly identify potential vulnerabilities in large codebases. She requires automated detection of security anti-patterns to ensure compliance with financial industry regulations.

## Key Requirements

1. **OWASP Top 10 vulnerability pattern detection with severity scoring**
   - Essential for identifying the most critical web application security risks that could compromise financial data. The severity scoring helps prioritize remediation efforts based on potential impact to financial systems.

2. **Cryptographic misuse detection including weak algorithms and hardcoded secrets**
   - Critical for fintech environments where encryption protects sensitive financial data. Detecting weak algorithms and hardcoded secrets prevents data breaches and ensures regulatory compliance.

3. **Input validation pattern analysis for SQL injection and XSS vulnerabilities**
   - Vital for protecting against data manipulation and theft in financial applications. These vulnerabilities could lead to unauthorized access to customer financial records or transaction manipulation.

4. **Compliance report generation with regulatory mapping (PCI-DSS, SOC2)**
   - Required for demonstrating adherence to financial industry standards. Automated mapping saves significant time during audit preparation and ensures no compliance requirements are missed.

5. **False positive suppression with audit trail for security exceptions**
   - Necessary for maintaining efficiency while preserving accountability. The audit trail ensures that suppressed findings are documented and can be reviewed during compliance audits.

## Technical Requirements

- **Testability Requirements**
  - All pattern detection algorithms must be unit testable with synthetic code samples
  - Compliance report generation must be verifiable through mock data scenarios
  - False positive suppression logic must be testable with documented test cases
  - Integration tests must verify end-to-end scanning of sample codebases

- **Performance Expectations**
  - Must scan 100,000 lines of code in under 5 minutes
  - Memory usage should not exceed 2GB for typical codebases
  - Incremental scanning should process only changed files
  - Report generation should complete within 30 seconds

- **Integration Points**
  - File system access for reading source code files
  - AST parsing for Python code analysis
  - JSON/XML output for integration with other security tools
  - Configuration file support for custom rule definitions

- **Key Constraints**
  - Must operate without network access for air-gapped environments
  - Should not modify source code files
  - Must handle malformed code gracefully without crashing
  - All processing must be deterministic for audit repeatability

**IMPORTANT:** The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The security vulnerability detection engine must provide:

1. **Pattern Detection Engine**
   - AST-based analysis for detecting security anti-patterns
   - Regular expression matching for finding hardcoded secrets
   - Data flow analysis for tracking user input to sensitive operations
   - Control flow analysis for identifying missing validation

2. **Vulnerability Assessment**
   - OWASP Top 10 pattern matching with configurable rules
   - Severity scoring based on CVSS methodology
   - Context-aware analysis to reduce false positives
   - Support for custom vulnerability patterns

3. **Compliance Mapping**
   - Automatic mapping of findings to PCI-DSS requirements
   - SOC2 control mapping for identified vulnerabilities
   - Customizable compliance framework support
   - Evidence collection for audit documentation

4. **Reporting System**
   - Structured JSON/XML reports for tool integration
   - Executive summary with risk metrics
   - Technical details with code locations and remediation guidance
   - Trend analysis for tracking security posture over time

5. **Exception Management**
   - Whitelist functionality for approved patterns
   - Suppression rules with expiration dates
   - Audit logging for all suppressed findings
   - Review workflow support for exception approval

## Testing Requirements

### Key Functionalities to Verify
- Accurate detection of all OWASP Top 10 vulnerability patterns
- Correct severity scoring based on vulnerability context
- Proper cryptographic misuse identification
- Comprehensive input validation vulnerability detection
- Accurate compliance mapping to regulatory frameworks

### Critical User Scenarios
- Scanning a complete fintech application codebase
- Generating compliance reports for PCI-DSS audit
- Suppressing false positives with proper documentation
- Re-scanning after remediation to verify fixes
- Analyzing code changes for new vulnerabilities

### Performance Benchmarks
- Scan 100,000 lines of code in under 5 minutes
- Generate compliance report in under 30 seconds
- Memory usage under 2GB for typical scans
- Support incremental scanning with 90% time reduction

### Edge Cases and Error Conditions
- Handling malformed Python code without crashing
- Processing files with encoding issues
- Managing extremely large files (>10MB)
- Dealing with circular imports and dependencies
- Recovering from file system access errors

### Required Test Coverage Metrics
- Minimum 90% code coverage for pattern detection logic
- 100% coverage for security-critical paths
- All OWASP patterns must have positive and negative test cases
- Each compliance mapping must be verified with test data
- Performance tests for scalability validation

**IMPORTANT:**
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches
- **REQUIRED:** Tests must be run with pytest-json-report to generate a pytest_results.json file:
  ```
  pip install pytest-json-report
  pytest --json-report --json-report-file=pytest_results.json
  ```
- The pytest_results.json file must be included as proof that all tests pass

## Success Criteria

The implementation successfully meets the security auditor's needs when:

1. **Detection Accuracy**
   - All OWASP Top 10 patterns are detected with >95% accuracy
   - False positive rate is below 10% for common patterns
   - No critical vulnerabilities are missed in test codebases

2. **Compliance Support**
   - Generated reports map to 100% of applicable PCI-DSS requirements
   - SOC2 control evidence is automatically collected
   - Audit trails meet regulatory documentation standards

3. **Performance Metrics**
   - Large codebases scan within performance benchmarks
   - Incremental scanning reduces analysis time by >80%
   - Memory usage remains within specified limits

4. **Operational Excellence**
   - Exception management provides clear audit trails
   - Reports are actionable with clear remediation guidance
   - Integration with existing security tools is seamless

**REQUIRED FOR SUCCESS:**
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

From within the project directory, set up the development environment:

```bash
# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

# Install project in development mode
uv pip install -e .
```

**REMINDER:** The implementation MUST emphasize that generating and providing pytest_results.json is a critical requirement for project completion.