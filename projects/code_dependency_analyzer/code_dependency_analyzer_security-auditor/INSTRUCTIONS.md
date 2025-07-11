# Security Dependency Chain Analyzer

## Overview
A specialized dependency analysis tool designed for cybersecurity consultants to trace untrusted input flows through code dependencies, identify supply chain vulnerabilities, and detect potential security risks in module import patterns.

## Persona Description
A cybersecurity consultant who examines codebases for supply chain vulnerabilities and insecure dependency patterns. They need to trace how untrusted input flows through dependencies.

## Key Requirements
1. **Taint analysis tracking through dependency chains**: The tool must trace how untrusted input propagates through function calls across module boundaries, identifying paths where user input could reach sensitive operations without proper validation or sanitization.

2. **Third-party dependency risk scoring with CVE integration**: Critical for supply chain security, the system must analyze all external dependencies, cross-reference them with CVE databases, and calculate risk scores based on vulnerability severity, dependency depth, and usage patterns.

3. **Privilege escalation path detection through imports**: Essential for identifying security boundaries, the tool must detect when low-privilege code imports high-privilege modules, analyzing capability escalation paths that could be exploited by malicious actors.

4. **Sandbox escape possibility analysis via module access**: To prevent containment breaches, the system must identify import patterns that could potentially bypass security sandboxes, including dynamic imports, reflection usage, and access to system-level modules.

5. **Supply chain attack vector identification**: Vital for comprehensive security assessment, the tool must map all dependency sources, identify potential typosquatting risks, detect suspicious package behaviors, and highlight dependencies with unusual permission requirements.

## Technical Requirements
- **Testability requirements**: All security analysis algorithms must be unit testable with mock vulnerability data and taint sources. Integration tests should verify detection of known vulnerability patterns.
- **Performance expectations**: Must analyze dependency chains of 1,000+ packages within 15 minutes. Taint analysis should handle call graphs with 100,000+ edges efficiently.
- **Integration points**: Must integrate with CVE databases (NVD, OSV), package registries (PyPI), and security scanning tools. Provide APIs for SAST tool integration.
- **Key constraints**: Must work with obfuscated code, handle dynamic analysis limitations, and provide meaningful results even with incomplete type information.

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The analyzer must perform static taint analysis across module boundaries, integrate with vulnerability databases for real-time risk assessment, detect privilege boundaries in import hierarchies, analyze dynamic import patterns for sandbox escapes, and generate detailed security reports with remediation recommendations. The system should support custom taint sources and sinks for domain-specific security policies.

## Testing Requirements
- **Key functionalities that must be verified**:
  - Accurate taint propagation through complex call chains
  - Correct CVE matching and risk score calculation
  - Reliable privilege escalation path detection
  - Proper identification of sandbox escape patterns
  - Accurate supply chain risk assessment

- **Critical user scenarios that should be tested**:
  - Tracing SQL injection vulnerabilities through ORM dependencies
  - Identifying backdoored packages in the dependency tree
  - Detecting privilege escalation from web handlers to system calls
  - Analyzing sandbox escape attempts through file system imports
  - Assessing supply chain risks in a machine learning pipeline

- **Performance benchmarks that must be met**:
  - Analyze 100 dependencies with CVE checks in under 60 seconds
  - Complete taint analysis for 10,000 functions in under 5 minutes
  - Process dependency trees with 1,000+ packages in under 15 minutes
  - Memory usage under 4GB for large enterprise applications

- **Edge cases and error conditions that must be handled properly**:
  - Obfuscated or minified Python code
  - Dependencies with no version information
  - Private package repositories
  - Circular dependency chains
  - Runtime-generated imports

- **Required test coverage metrics**:
  - Minimum 95% code coverage for taint analysis engine
  - 100% coverage for CVE integration modules
  - Full coverage of privilege escalation detection
  - Integration tests for all supported vulnerability databases

IMPORTANT:
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches
- REQUIRED: Tests must be run with pytest-json-report to generate a pytest_results.json file:
  ```
  pip install pytest-json-report
  pytest --json-report --json-report-file=pytest_results.json
  ```
- The pytest_results.json file must be included as proof that all tests pass

## Success Criteria
Clear metrics and outcomes that would indicate the implementation successfully meets this persona's needs:
- Detects 90% of OWASP Top 10 vulnerability patterns in dependencies
- Identifies 95% of known vulnerable packages through CVE integration
- Traces taint propagation with less than 10% false positive rate
- Discovers all privilege escalation paths in test applications
- Reduces supply chain attack surface by identifying 80% of risky dependencies

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup
From within the project directory, set up the development environment:
```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```