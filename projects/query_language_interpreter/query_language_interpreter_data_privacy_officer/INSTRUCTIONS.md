# Privacy-Focused Data Query Interpreter

A specialized query language interpreter for privacy compliance auditing with features for PII detection, data minimization, access logging, policy enforcement, and anonymization.

## Overview

This project implements a query language interpreter designed for data privacy officers who need to audit and ensure data protection compliance across company systems. It allows privacy officers to identify, analyze, and protect personal information without centralizing sensitive data. The interpreter includes robust PII detection, policy enforcement, access logging, and anonymization capabilities essential for compliance with modern data protection regulations.

## Persona Description

Raj ensures compliance with data protection regulations across company systems. He needs to query data repositories to identify personal information without centralizing sensitive data in additional systems.

## Key Requirements

1. **PII Detection Using Pattern Matching and Validation**
   - Implement pattern recognition for common PII types (SSNs, credit cards, emails, addresses, etc.)
   - Support validation algorithms for PII formats (checksum validation, format verification)
   - Enable detection of PII in unstructured text and structured data fields
   - Include confidence scoring for potential PII matches
   - Critical for Raj to identify personal data across various systems to ensure it is properly protected and documented in accordance with regulations

2. **Data Minimization Filtering**
   - Automatically filter query results to show only essential fields needed for compliance reviews
   - Support role-based field visibility profiles for different compliance functions
   - Enable progressive disclosure showing minimal data first with drill-down capabilities
   - Include justification tracking for each field accessed in compliance reviews
   - Essential for applying data minimization principles required by regulations, ensuring reviewers see only the data necessary for their specific compliance task

3. **Access Logging with Immutable Records**
   - Create tamper-evident logs of all queries against sensitive data
   - Record query details including user, timestamp, purpose, data accessed, and results count
   - Support cryptographic verification of log integrity
   - Enable log analysis for access pattern monitoring
   - Crucial for demonstrating compliance with regulations requiring accountability and auditability of all access to personal data

4. **Policy-Based Query Restrictions**
   - Enforce data access policies through query validation before execution
   - Prevent unauthorized data combinations that could lead to re-identification
   - Support purpose limitation constraints requiring query justification
   - Enable data retention policies that restrict access to expired data
   - Important for implementing privacy by design principles and ensuring queries comply with organizational policies and regulatory requirements

5. **Anonymization Functions**
   - Automatically mask sensitive fields in query results based on policy rules
   - Support various anonymization techniques (hashing, tokenization, generalization, etc.)
   - Include k-anonymity and differential privacy implementations
   - Maintain consistency of anonymized values within result sets
   - Critical for allowing useful data analysis while protecting individual privacy and complying with data protection regulations

## Technical Requirements

### Testability Requirements
- PII detection algorithms must be testable with synthetic personal data
- Policy enforcement must block predefined non-compliant queries
- Access logs must be verifiably complete and tamper-evident
- Anonymization techniques must be evaluated for re-identification risk
- All components must work with test data that doesn't contain actual PII

### Performance Expectations
- Scan 1 million records for PII in under 5 minutes
- Apply policy restrictions with negligible query latency (under 100ms)
- Generate and verify access logs with minimal performance impact
- Complete anonymization of large result sets (100k+ records) in under 30 seconds
- Support concurrent compliance queries without significant performance degradation

### Integration Points
- Connect to various data sources (databases, file systems, cloud storage)
- Export compliance reports in standard formats (CSV, PDF, XLSX)
- Integration with identity and access management systems
- Hooks for custom PII detection rules
- API access for compliance monitoring tools

### Key Constraints
- Must not create additional copies of sensitive data
- All operations must maintain data locality when possible
- Access controls must be strictly enforced at all levels
- No cloud dependencies for core privacy functions
- Must support operation in heavily regulated industries

## Core Functionality

The core of this Query Language Interpreter includes:

1. **PII Detection Engine**
   - Pattern-based recognition of common PII types
   - Validation algorithms for data format verification
   - Context-aware detection in unstructured content
   - Confidence scoring for potential matches

2. **Query Control System**
   - Policy enforcement before query execution
   - Purpose limitation validation
   - Prevention of unauthorized data combinations
   - Role-based access controls

3. **Audit Logger**
   - Cryptographically secured access records
   - Complete query metadata capture
   - Tamper-evident log storage
   - Access pattern analysis tools

4. **Privacy-Preserving Query Processor**
   - Data minimization by default
   - Field-level access controls
   - Progressive disclosure mechanisms
   - Query result filtering

5. **Anonymization Engine**
   - Multiple anonymization techniques
   - Consistency preservation in result sets
   - Re-identification risk assessment
   - Privacy/utility tradeoff controls

## Testing Requirements

### Key Functionalities to Verify
- Accurate detection of all PII types in test datasets
- Correct enforcement of access control policies
- Complete and tamper-evident logging of all query activities
- Proper data minimization in query results
- Effective anonymization while maintaining data utility

### Critical User Scenarios
- Conducting a GDPR data subject access request across systems
- Performing a PII inventory across company data repositories
- Investigating a potential data breach for exposed personal information
- Preparing anonymized datasets for third-party analysis
- Documenting compliance with data protection regulations

### Performance Benchmarks
- PII scan rate of at least 10MB/second
- Policy enforcement overhead under 5% of query time
- Access log verification in under 100ms
- Anonymization processing at 10,000 records/second
- Support for datasets up to 100GB without requiring sampling

### Edge Cases and Error Conditions
- Handling near-matches and edge cases in PII detection
- Managing conflicting policy rules gracefully
- Preserving access logs during system failures
- Detecting attempts to circumvent privacy controls
- Maintaining anonymization consistency with incremental data

### Required Test Coverage Metrics
- 100% coverage for policy enforcement code
- 95% coverage for PII detection algorithms
- Comprehensive tests for anonymization functions
- Verification of all access logging scenarios
- Security testing for potential privacy vulnerabilities

## Success Criteria

1. All regulated PII types are correctly identified across test datasets
2. Policy-violating queries are consistently blocked
3. Access logs provide complete audit trails that pass integrity verification
4. Data minimization limits exposed fields to only those necessary
5. Anonymized data maintains utility while protecting privacy
6. System passes simulated regulatory compliance audits
7. Privacy officers can perform their duties without creating additional data copies
8. Query results can be used to demonstrate compliance with regulations

## Getting Started with Development

To start developing this project:

1. Set up the development environment using `uv`:
   ```
   uv init --lib
   ```

2. Manage dependencies with `uv`:
   ```
   uv pip install pandas cryptography
   ```

3. Run your code with:
   ```
   uv run python your_script.py
   ```

4. Run tests with:
   ```
   uv run pytest
   ```