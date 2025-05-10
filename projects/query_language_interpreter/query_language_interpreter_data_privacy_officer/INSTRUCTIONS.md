# Privacy-Focused Data Query Engine

A query language interpreter specialized for data privacy compliance without centralizing sensitive information.

## Overview

The Privacy-Focused Data Query Engine provides a specialized query system for identifying, analyzing, and protecting personal information across company systems. This project variant focuses on enabling compliance with data protection regulations without centralizing sensitive data, featuring advanced PII detection, data minimization, and policy-based query restrictions.

## Persona Description

Raj ensures compliance with data protection regulations across company systems. He needs to query data repositories to identify personal information without centralizing sensitive data in additional systems.

## Key Requirements

1. **PII (Personally Identifiable Information) detection using pattern matching and validation**
   - Implement comprehensive pattern recognition for various PII types (names, addresses, government IDs, financial information)
   - Support validation rules to reduce false positives in PII detection
   - Enable configurable sensitivity levels for different types of identification
   - Add regional variants for PII formats across different countries and regulations
   - Critical for Raj to systematically identify all locations where personal data exists across disparate systems

2. **Data minimization filtering showing only essential fields for compliance reviews**
   - Develop automated field filtering based on purpose specification
   - Support role-based minimization profiles with different access levels
   - Implement field-level redaction and masking based on query purpose
   - Enable audit trails documenting minimization decisions
   - Essential for demonstrating compliance with data minimization principles and limiting exposure of sensitive information

3. **Access logging creating immutable records of all queries against sensitive data**
   - Create tamper-evident logs of all access to sensitive data
   - Record query details, user identity, purpose, timestamp, and accessed fields
   - Support cryptographic verification of log integrity
   - Enable automated suspicious access pattern detection
   - Critical for compliance with regulatory requirements for tracking and justifying all access to personal data

4. **Policy-based query restrictions preventing unauthorized data combinations**
   - Implement a rules engine for enforcing data usage policies
   - Support prohibition of certain field combinations that could lead to re-identification
   - Enable purpose-based restrictions on query patterns
   - Provide clear explanations when queries are rejected
   - Vital for preventing accidental or deliberate circumvention of privacy protections

5. **Anonymization functions automatically masking sensitive fields in query results**
   - Develop techniques for various anonymization methods (masking, tokenization, generalization, perturbation)
   - Support k-anonymity and differential privacy techniques
   - Enable context-aware anonymization based on query purpose and data sensitivity
   - Provide anonymization strength metrics
   - Important for allowing useful analysis while maintaining individual privacy

## Technical Requirements

### Testability Requirements
- All privacy functions must be unit-testable with pytest
- Test PII detection accuracy against labeled datasets
- Verify policy enforcement with comprehensive test cases
- Test anonymization effectiveness using re-identification risk metrics
- Validate logging integrity with cryptographic verification

### Performance Expectations
- Scan data sources at rates exceeding 50MB/second for PII
- Apply policy restrictions with minimal query latency (under 100ms overhead)
- Process anonymization functions with less than 5% performance impact
- Support incremental scanning of large datasets (multi-TB)
- Complete privacy impact assessments on 1GB datasets in under 10 minutes

### Integration Points
- Connect to common data storage systems (databases, file systems, object storage)
- Support common data formats (CSV, JSON, XML, database tables)
- Integrate with identity and access management systems
- Provide audit output compatible with compliance reporting tools
- Enable policy synchronization with centralized governance systems

### Key Constraints
- Never create persistent copies of sensitive data during processing
- Enforce strict memory management to prevent data leakage
- Support air-gapped operation in high-security environments
- Minimize false positives in PII detection while maintaining high recall
- Ensure all operations are explainable for compliance justification

### Implementation Notes
IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Privacy-Focused Data Query Engine must implement the following core functionality:

1. **Data Discovery and Classification**
   - Scan various data sources to identify PII and sensitive information
   - Classify detected information according to sensitivity and risk
   - Maintain data maps linking sensitive information to storage locations
   - Update classifications incrementally as data changes

2. **Privacy-Enhanced Query Processing**
   - Parse and analyze queries for privacy implications
   - Apply policy-based restrictions to prevent privacy violations
   - Transform queries to incorporate data minimization
   - Implement privacy-preserving joins and aggregations

3. **Anonymization Engine**
   - Apply appropriate anonymization techniques based on context
   - Support various methods from simple masking to differential privacy
   - Evaluate and report re-identification risk
   - Preserve data utility while enhancing privacy

4. **Audit and Compliance System**
   - Record detailed logs of all sensitive data access
   - Protect logs from tampering or unauthorized access
   - Generate compliance reports for various regulations
   - Detect anomalous access patterns

5. **Policy Enforcement Framework**
   - Define and manage data usage policies
   - Evaluate queries against established policies
   - Provide clear feedback for policy violations
   - Support policy version control and change management

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of PII detection across different data formats
- Correct application of data minimization based on purpose
- Reliable enforcement of policy-based restrictions
- Effectiveness of anonymization techniques
- Integrity and completeness of access logging

### Critical User Scenarios
- Conducting a data protection impact assessment across enterprise systems
- Identifying all instances of specific PII types for right-to-be-forgotten requests
- Analyzing customer data for marketing purposes while preserving privacy
- Investigating a security incident without exposing additional sensitive data
- Providing evidence of compliance during a regulatory audit

### Performance Benchmarks
- Detect PII in unstructured text at a rate of at least 50MB per second
- Process policy evaluation for complex queries in under 100ms
- Apply anonymization to 1 million records in under 30 seconds
- Scale to handle enterprise datasets of 100+ TB with distributed processing
- Support concurrent queries from at least 50 compliance team members

### Edge Cases and Error Conditions
- Handling encrypted or encoded data during PII scanning
- Managing conflicting or ambiguous policy rules
- Processing datasets with extremely high PII density
- Dealing with attempts to circumvent policy restrictions
- Recovering from interrupted scans of large datasets

### Required Test Coverage Metrics
- Minimum 95% code coverage for all privacy-critical functions
- Test all PII detection patterns against at least 1,000 positive and negative examples
- 100% coverage of policy enforcement logic
- Verify anonymization functions against known re-identification attacks
- Test logging integrity with simulated tampering attempts

## Success Criteria

The implementation will be considered successful if it meets the following criteria:

1. **Functional Completeness**
   - All five key requirements are fully implemented
   - PII detection achieves >95% recall and >90% precision on test datasets
   - Policy restrictions correctly prevent all tested privacy violations
   - Anonymization techniques demonstrably reduce re-identification risk
   - Access logging creates verifiably complete and tamper-evident records

2. **Compliance Effectiveness**
   - Supports compliance with major privacy regulations (GDPR, CCPA/CPRA, HIPAA)
   - Enables data mapping required for regulatory reporting
   - Provides necessary evidence for demonstrating compliance
   - Significantly reduces manual effort in compliance processes

3. **Security and Privacy Protection**
   - Does not introduce new privacy or security risks
   - Successfully prevents unauthorized data combinations
   - Applies appropriate minimization and anonymization
   - Maintains secure handling of sensitive data throughout processing

4. **Operational Feasibility**
   - Functions without creating additional copies of sensitive data
   - Performs efficiently enough for regular enterprise use
   - Scales appropriately with data volume
   - Integrates with existing data infrastructure