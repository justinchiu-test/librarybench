# PyPatternGuard - Healthcare Compliance Pattern Detection Engine

## Overview
A specialized code pattern detection system designed for compliance officers in healthcare organizations to ensure code meets HIPAA requirements and medical device regulations. The system detects privacy violations, validates compliance patterns, and tracks regulatory adherence.

## Persona Description
A compliance officer in healthcare who ensures code meets HIPAA requirements and medical device regulations. He needs specialized pattern detection for healthcare-specific security and privacy concerns.

## Key Requirements

1. **PHI data flow analysis to detect potential privacy leaks**: Critical for HIPAA compliance by tracking how Protected Health Information flows through the system and identifying potential exposure points where data could be leaked or accessed inappropriately.

2. **Medical device software pattern compliance (IEC 62304)**: Essential for ensuring software controlling or interacting with medical devices follows required safety patterns and development lifecycle requirements mandated by international standards.

3. **Audit logging pattern verification for compliance tracking**: Validates that all access to sensitive data is properly logged with required details (who, what, when, where, why) to meet regulatory audit requirements and enable forensic analysis.

4. **Data retention policy pattern enforcement**: Ensures implementation follows legal requirements for data retention and deletion, including automatic purging of expired data and proper archival procedures for different data classifications.

5. **Regulatory change impact analysis on existing patterns**: Provides assessment of how new or updated regulations impact existing code patterns, helping prioritize remediation efforts and maintain continuous compliance.

## Technical Requirements

### Testability Requirements
- All compliance checks must produce deterministic, auditable results
- Support for creating test scenarios with synthetic PHI data
- Ability to simulate various regulatory contexts and requirements
- Clear audit trail generation for all analysis operations

### Performance Expectations
- Complete compliance scan of 500,000 lines of code within 10 minutes
- Real-time pattern detection for CI/CD integration
- Low memory footprint to run alongside other compliance tools
- Incremental scanning capability for large healthcare systems

### Integration Points
- AST analysis using Python's `ast` module
- Data flow analysis using control flow graphs
- Configuration via JSON/YAML for regulatory rules
- Export to compliance reporting formats (CSV, JSON, XML)

### Key Constraints
- Must work with Python 3.8+ healthcare applications
- No external dependencies beyond Python standard library
- Must handle sensitive data without storing or exposing it
- Analysis must be read-only with no system modifications

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide:

1. **PHI Data Flow Analyzer**: Tracks the flow of PHI through the codebase by identifying data sources, transformations, and sinks, using taint analysis to detect potential leakage points and unauthorized access patterns.

2. **Medical Device Compliance Checker**: Validates code against IEC 62304 requirements including proper error handling, safety-critical function isolation, and required documentation patterns in code comments and structure.

3. **Audit Trail Verifier**: Analyzes logging implementations to ensure all PHI access is logged with required fields, validates log immutability patterns, and checks for proper log retention and protection mechanisms.

4. **Data Retention Policy Analyzer**: Identifies data storage patterns, validates automatic deletion mechanisms, ensures proper data classification handling, and detects violations of retention period requirements.

5. **Regulatory Impact Assessor**: Maps existing code patterns to regulatory requirements, identifies areas affected by regulatory changes, provides risk scoring for non-compliant patterns, and generates remediation priority lists.

## Testing Requirements

### Key Functionalities to Verify
- Accurate PHI data flow tracking through complex call chains
- Correct identification of IEC 62304 compliance violations
- Comprehensive audit logging pattern detection
- Data retention policy enforcement validation
- Regulatory mapping accuracy and completeness

### Critical User Scenarios
- Analyzing a hospital management system for HIPAA compliance
- Validating medical device software before FDA submission
- Auditing data retention practices across multiple services
- Assessing impact of new privacy regulations on existing code
- Generating compliance reports for regulatory audits

### Performance Benchmarks
- PHI flow analysis: < 2 seconds per 1,000 lines of code
- Compliance pattern matching: < 100ms per pattern per file
- Audit trail verification: < 1 second per service module
- Full compliance scan of 100,000 LOC: < 3 minutes
- Regulatory impact analysis: < 5 minutes for complete codebase

### Edge Cases and Error Conditions
- Obfuscated or encrypted data handling code
- Dynamic data access patterns using reflection
- Third-party library interactions with PHI
- Complex inheritance hierarchies affecting data access
- Incomplete code with compliance-critical sections missing

### Required Test Coverage Metrics
- Line coverage: minimum 95% (compliance-critical code: 100%)
- Branch coverage: minimum 90%
- All HIPAA safeguards must have dedicated test cases
- All IEC 62304 requirements must be testable
- Integration tests covering multi-service PHI flows

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

The implementation successfully meets this persona's needs when:

1. **Compliance Accuracy**: The system identifies 99% of known compliance violations in test healthcare codebases with less than 1% false positives.

2. **Regulatory Coverage**: All major HIPAA technical safeguards and IEC 62304 requirements are covered by detection patterns.

3. **Audit Readiness**: Generated reports meet requirements for regulatory audits and can be directly submitted as compliance evidence.

4. **Risk Mitigation**: The system provides clear risk scores and remediation priorities that align with regulatory enforcement guidelines.

5. **Continuous Compliance**: Integration with CI/CD pipelines prevents non-compliant code from reaching production environments.

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

From within the project directory, set up the virtual environment:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```

Run tests with pytest-json-report:
```
uv pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```