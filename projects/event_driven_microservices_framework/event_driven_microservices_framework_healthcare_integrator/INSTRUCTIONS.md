# Healthcare Data Integration Microservices Framework

## Overview
This project is a specialized event-driven microservices framework designed for healthcare environments that prioritizes patient data privacy, secure information sharing, and regulatory compliance. It provides field-level encryption, consent-based information sharing, emergency access patterns, and compliance validation to enable secure, compliant data exchange between healthcare systems.

## Persona Description
Dr. Chen coordinates integration between various healthcare systems in a hospital network where patient data must flow securely between services. Her primary goal is to implement a compliant microservices framework that ensures patient data privacy while enabling critical information sharing between departments and systems.

## Key Requirements

1. **PHI (Protected Health Information) Data Handling with Field-level Encryption**
   - Implement field-level encryption for sensitive patient health information
   - Create key management for secure data access by authorized services
   - Support for data anonymization and de-identification where appropriate
   - Include security audit logging for all PHI access
   - This feature is critical for HIPAA compliance and protecting patient privacy in distributed healthcare systems

2. **Consent-based Information Sharing with Patient-specific Routing Rules**
   - Develop patient consent management for selective data sharing
   - Create dynamic routing rules based on patient consent preferences
   - Support for consent expiration and revocation
   - Include granular control over specific data elements shared
   - This feature ensures patient data is only shared according to their explicit consent and preferences

3. **Emergency Override Patterns with Security Audit Logging**
   - Implement emergency access override mechanisms for critical care situations
   - Create comprehensive security audit logging for all override instances
   - Support for post-access justification documentation
   - Include notification systems for privacy officers
   - This feature enables access to critical information in emergencies while maintaining accountability

4. **Regulatory Compliance Validation for Healthcare Data Exchange**
   - Develop compliance rule engines for HIPAA, GDPR, and other healthcare regulations
   - Create validation tools for data exchange compliance
   - Support for compliance reporting and documentation
   - Include version tracking of compliance rules as regulations evolve
   - This feature ensures all data exchanges meet relevant healthcare regulatory requirements

5. **System of Record Designation with Authoritative Data Sourcing**
   - Implement system of record designation for each data category
   - Create conflict resolution rules when multiple sources exist
   - Support for data lineage tracking across systems
   - Include data synchronization protocols for system of record updates
   - This feature establishes clear data ownership and authoritative sources for consistent patient information

## Technical Requirements

### Testability Requirements
- Support for compliance validation testing
- Ability to simulate various consent scenarios
- Testing of emergency access patterns
- Verification of data encryption and security mechanisms

### Performance Expectations
- Maximum 200ms latency for patient data requests (non-emergency)
- Maximum 50ms latency for emergency data access
- Support for at least 1,000 concurrent healthcare providers
- Ability to process and route 10,000+ healthcare events per minute

### Integration Points
- Integration with Electronic Health Record (EHR) systems
- Support for healthcare data standards (HL7, FHIR, DICOM)
- Compatibility with identity management and access control systems
- Integration with existing healthcare analytics platforms

### Key Constraints
- Must comply with all relevant healthcare regulations (HIPAA, GDPR, etc.)
- Must provide complete audit trails for all PHI access
- Must support emergency access without compromising security
- Must maintain data integrity across integrated systems

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The framework must provide:

1. **Secure Data Management**
   - Field-level encryption and decryption
   - Key management and access control
   - Data anonymization and de-identification
   - Security audit logging

2. **Consent Management**
   - Patient consent recording and enforcement
   - Consent-based routing rules
   - Granular data sharing controls
   - Consent lifecycle management

3. **Emergency Access System**
   - Break-glass procedures for emergency access
   - Comprehensive security audit logging
   - Post-access justification workflow
   - Notification and alerting

4. **Compliance Engine**
   - Regulatory rule implementation and enforcement
   - Compliance validation for data exchanges
   - Compliance reporting and documentation
   - Rule versioning and updates

5. **Data Authority Management**
   - System of record designation
   - Conflict resolution mechanisms
   - Data lineage tracking
   - Synchronization protocols

## Testing Requirements

### Key Functionalities that Must be Verified
- PHI encryption and protection throughout the system
- Consent-based routing and information sharing
- Emergency access override functionality
- Regulatory compliance validation
- System of record designation and conflict resolution

### Critical User Scenarios
- Patient data exchange between hospital departments
- Emergency access to critical patient information
- Consent changes affecting data availability
- Regulatory compliance auditing
- Reconciliation of conflicting patient data from multiple sources

### Performance Benchmarks
- Process 10,000+ healthcare events per minute
- Maintain patient data request latency under 200ms
- Support 1,000+ concurrent healthcare providers
- Complete compliance validation within 100ms per transaction

### Edge Cases and Error Conditions
- Emergency access during system degradation
- Conflicting consent directives
- Incomplete or corrupted PHI data
- Regulatory requirement conflicts
- System of record unavailability

### Required Test Coverage Metrics
- Minimum 95% line coverage for all code
- 100% coverage of PHI handling and encryption
- 100% coverage of consent management functionality
- 100% coverage of emergency access patterns
- 100% coverage of compliance validation logic

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

The implementation will be considered successful if:

1. PHI data is securely handled with appropriate encryption
2. Patient consent directives are properly enforced for data sharing
3. Emergency access functions correctly with proper audit logging
4. Compliance validation ensures regulatory requirements are met
5. System of record designation correctly establishes data authority
6. Performance meets the specified benchmarks
7. All test cases pass with the required coverage

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

### Development Environment Setup

To set up the development environment:

```bash
# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install the project in development mode
uv pip install -e .

# Install test dependencies
uv pip install pytest pytest-json-report

# Run tests and generate the required JSON report
pytest --json-report --json-report-file=pytest_results.json
```

CRITICAL: Generating and providing the pytest_results.json file is a mandatory requirement for project completion. This file serves as evidence that all functionality has been implemented correctly and passes all tests.