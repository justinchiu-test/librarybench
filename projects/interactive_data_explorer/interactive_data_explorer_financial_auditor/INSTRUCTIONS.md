# Financial Transaction Audit Explorer

## Overview
A specialized terminal-based data exploration framework designed for financial auditors who need to securely analyze transaction patterns, identify irregularities, and maintain a complete audit trail without exposing sensitive financial data. This tool enables thorough forensic analysis of financial records while adhering to regulatory requirements.

## Persona Description
Sophia conducts financial audits examining transaction patterns to identify potential irregularities. She requires secure data exploration capabilities that maintain chain of custody while highlighting statistical outliers in financial datasets.

## Key Requirements
1. **Benford's Law analysis** - Automatically detect potentially fraudulent numerical distributions that deviate from expected natural number patterns. This statistical technique is essential for auditors to quickly flag data sets that may contain manipulated values, as legitimate financial data typically follows Benford's distribution.

2. **Transaction flow visualization** - Generate clear representations showing money movement between accounts and entities to reveal unusual patterns or circular transactions. Auditors need to trace complex financial relationships and identify suspicious patterns that may indicate money laundering or other financial improprieties.

3. **Temporal pattern detection** - Highlight unusual timing patterns in financial activities such as transactions that occur outside business hours, at regular intervals suggesting automation, or in unusual sequences. Timing anomalies often provide critical clues to fraudulent or improper activities.

4. **Audit trail documentation** - Automatically record all data transformations and findings, essential for maintaining a legally defensible chain of evidence. Financial auditors must document every step of their analysis process to ensure findings can withstand legal scrutiny and demonstrate due diligence.

5. **Regulatory framework templates** - Apply specific compliance rules to different financial sectors (banking, insurance, investments) to automate checking for violations of relevant regulations. Auditors must efficiently verify compliance with industry-specific rules that vary across different financial domains.

## Technical Requirements
- **Testability Requirements**:
  - All statistical methods must be verifiable against established financial forensic techniques
  - Transaction flow algorithms must be tested with known fraudulent pattern datasets
  - Temporal pattern detection must reliably identify known suspicious timing patterns
  - Audit trail mechanisms must be verified for completeness and accuracy
  - Regulatory framework templates must correctly implement current compliance rules

- **Performance Expectations**:
  - Must handle datasets with up to 10 million transactions
  - Statistical analysis should complete within 30 seconds for datasets of 1 million records
  - Transaction flow visualization generation should complete within 10 seconds
  - Memory usage must remain below 4GB even with large datasets
  - All operations must maintain data integrity with cryptographic verification

- **Integration Points**:
  - Support for common financial data formats (CSV, XLSX, JSON, bank statement exports)
  - Export functionality for standard audit documentation formats
  - Integration with regulatory compliance databases and rule sets
  - Support for cryptographically signing analysis results for legal purposes

- **Key Constraints**:
  - No external network access during analysis to maintain data security
  - All processed data must remain in secure memory without touching disk
  - All operations must be traceable and logged for chain of custody
  - Must function in secure environments with limited system access
  - No sharing or exporting of raw data outside the controlled environment

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The Financial Transaction Audit Explorer must provide a comprehensive framework for financial forensic analysis:

1. **Statistical Analysis and Fraud Detection**:
   - Implement Benford's Law analysis for first, second, and digit pair distributions
   - Calculate Z-scores and p-values for statistical deviation from expected patterns
   - Apply other statistical tests (zero/duplicate analysis, round number frequency)
   - Generate statistical profiles of normal behavior for different transaction types
   - Identify outliers and anomalies based on multiple statistical measures

2. **Transaction Network Analysis**:
   - Build directed graphs of money movement between accounts and entities
   - Identify circular transaction patterns and unusual relationship structures
   - Calculate network centrality measures to find key accounts
   - Detect unusual transaction paths that may indicate layering
   - Visualize transaction networks using terminal-friendly representations

3. **Temporal Analysis**:
   - Identify transactions occurring at unusual times or with suspicious timing patterns
   - Detect abnormal frequencies, periodicities, or rhythms in transaction timing
   - Analyze transaction velocity and volume changes over time
   - Identify correlation with external events or end-of-period activities
   - Flag transactions that violate expected business hours or processing cycles

4. **Audit Trail and Documentation**:
   - Maintain cryptographically secure logs of all analysis operations
   - Record data provenance and all transformations with timestamps
   - Generate detailed finding reports with supporting evidence
   - Implement chain-of-custody records for all data handled
   - Provide exportable audit records suitable for legal proceedings

5. **Regulatory Compliance Analysis**:
   - Incorporate rule templates for various financial sectors (banking, insurance, securities)
   - Check transactions against suspicious activity thresholds
   - Verify compliance with sector-specific regulations
   - Identify potential regulatory violations with supporting evidence
   - Track regulation versions to ensure correct rules are applied based on transaction dates

## Testing Requirements
- **Key Functionalities to Verify**:
  - Benford's Law analysis correctly identifies known fraudulent datasets
  - Transaction flow visualization accurately represents complex money movements
  - Temporal pattern detection identifies known suspicious timing patterns
  - Audit trail completely and accurately records all analysis activities
  - Regulatory framework templates correctly flag non-compliant transactions

- **Critical User Scenarios**:
  - Loading and analyzing a large transaction dataset for fraud indicators
  - Tracing complex transaction flows between multiple entities
  - Identifying suspicious timing patterns across different transaction types
  - Generating complete audit documentation for legal proceedings
  - Applying sector-specific regulatory checks to financial data

- **Performance Benchmarks**:
  - Process and analyze 1 million transactions within 1 minute
  - Generate transaction flow network for 10,000 entities within 20 seconds
  - Complete temporal pattern analysis for 5 years of daily data within 30 seconds
  - Maintain real-time audit logging with negligible performance impact
  - Memory usage below 4GB with 10 million transaction dataset

- **Edge Cases and Error Conditions**:
  - Handling incomplete transaction records with missing fields
  - Processing malformed or inconsistent date formats
  - Managing extremely large connected components in transaction networks
  - Dealing with transactions spanning multiple reporting periods
  - Graceful degradation when approaching memory limits

- **Required Test Coverage Metrics**:
  - 95% code coverage for all core functionality
  - 100% coverage for audit trail and evidence preservation functions
  - All statistical methods validated against known datasets with established results
  - All regulatory rule implementations verified against actual regulation text
  - Complete integration tests for all public APIs

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
A successful implementation of the Financial Transaction Audit Explorer will demonstrate:

1. Accurate identification of statistical anomalies in financial data using Benford's Law
2. Clear visualization of complex transaction flows revealing suspicious patterns
3. Reliable detection of temporal anomalies in transaction timing
4. Complete and cryptographically secure audit trail functionality
5. Correct implementation of regulatory compliance checks for various financial sectors

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

To set up the development environment, use:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```