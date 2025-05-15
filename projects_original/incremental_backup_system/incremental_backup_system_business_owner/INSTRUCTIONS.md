# SecureBackup - Compliant Backup System for Small Business Accounting

## Overview
An incremental backup system tailored for small business owners who need secure, compliant backups of financial data. The system enables maintaining regulatory compliance, ensures proper retention policies for different types of financial documents, and provides a user-friendly interface for non-technical staff to verify and restore backups.

## Persona Description
Priya runs a small accounting firm and must maintain secure, compliant backups of client financial data. She needs a system that ensures regulatory compliance while being simple enough for non-technical staff to verify backups are working properly.

## Key Requirements
1. **Compliance-oriented Retention Policies**: Implement configurable retention policies that follow financial regulations for different document types. This feature allows Priya to set different retention periods based on document classification (tax records, invoices, payroll, etc.), ensuring regulatory compliance while automatically managing the backup lifecycle.

2. **Tamper-evident Backup Verification**: Create a system for generating cryptographic verification certificates after each successful backup. This capability provides Priya with auditable proof that backups were completed successfully and have not been altered, which is critical for demonstrating compliance during audits.

3. **Simplified Restoration Interface**: Design a straightforward restoration mechanism with clear search, preview, and recovery options. This feature enables non-technical staff to locate and restore specific documents or sets of files without requiring deep technical knowledge, reducing dependence on IT specialists.

4. **Role-based Access Controls**: Implement a permission system that allows different levels of access for backup administration and restoration privileges. This allows Priya to delegate backup verification tasks to staff members while restricting sensitive operations like policy modifications to authorized administrators.

5. **Automated Compliance Reporting**: Develop functionality to generate comprehensive reports documenting backup status, retention adherence, and access logs. These reports provide clear documentation of the backup system's compliance with financial regulations, simplifying audit preparation and regulatory documentation.

## Technical Requirements

### Testability Requirements
- All components must have isolated unit tests with dependency injection for external systems
- Retention policy engine must be tested with accelerated time simulation
- Cryptographic verification must be testable with predetermined inputs and expected outputs
- Restoration interface logic must be testable without actual file operations
- Access control system must verify proper authorization for all operations
- Report generation must be testable with mock backup history data

### Performance Expectations
- The system must efficiently handle incremental backups of at least 100,000 files (approximately 500GB)
- File deduplication must achieve at least 40% space reduction for typical financial document sets
- Backup operations must complete within a 4-hour window for initial backups
- Incremental backups should complete within 30 minutes for typical daily changes
- Report generation must complete in under 60 seconds for a full year of backup history
- Restoration operations must locate files within 5 seconds and begin restoration within 10 seconds

### Integration Points
- File system monitoring for real-time change detection
- Secure storage backends (local, network, and optional cloud storage)
- Cryptographic libraries for tamper-evident verification
- Authentication systems for role-based access
- Document classification system for retention policy application
- Notification systems for backup status and compliance alerts

### Key Constraints
- The implementation must be portable across Windows, macOS, and Linux
- All sensitive data must be encrypted both in transit and at rest
- The system must operate without requiring administrative privileges
- Compliance functionality must be configurable for different regulatory frameworks
- Operations must be fully auditable with immutable logs
- Resource usage must be throttled to avoid impacting normal business operations

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core of this implementation centers on a Python library that provides:

1. **Incremental Backup Engine**: A core module handling file change detection, efficient delta storage, and space-optimized backup creation with proper metadata preservation.

2. **Compliance Policy Manager**: A component that implements and enforces retention rules based on document classification, ensuring regulatory requirements are met while minimizing storage usage.

3. **Cryptographic Verification System**: Functionality to generate and validate tamper-evident certificates for all backup operations, providing verifiable proof of data integrity.

4. **Role-based Permission Framework**: A flexible permission system controlling access to backup operations, restoration capabilities, and administrative functions based on assigned roles.

5. **Document Classification Engine**: Logic to categorize documents based on content analysis, metadata, or explicit tagging to apply appropriate retention and security policies.

6. **Compliance Reporting Generator**: A component that produces comprehensive audit-ready reports documenting backup status, policy adherence, and system activity.

The system should be designed as a collection of Python modules with clear interfaces between components, allowing them to be used independently or as an integrated solution. All functionality should be accessible through a programmatic API that could be called by a UI tool (though implementing the UI itself is not part of this project).

## Testing Requirements

### Key Functionalities to Verify
- Incremental backup creation, verification, and restoration with data integrity checks
- Proper application of retention policies based on document classification
- Cryptographic verification of backup integrity with tamper detection
- Role-based access control for all backup and restoration operations
- Accurate compliance report generation with all required regulatory elements
- Efficient delta storage with appropriate deduplication for financial documents

### Critical User Scenarios
- Complete backup lifecycle from initial full backup to incremental updates to restoration
- Regulatory audit scenario requiring verification of backup integrity and retention compliance
- Delegation of backup verification and restoration tasks to non-technical staff
- Recovery from inadvertent deletion or modification of business-critical financial documents
- Handling of increasing data volume as the business grows over time

### Performance Benchmarks
- Initial backup rate of at least 200 files per second
- Incremental backup identification completing in under 30 seconds for 100,000 files
- Storage efficiency achieving at least 4:1 compression ratio for typical financial document sets
- Search operations returning results in under 3 seconds for complex queries
- Restoration operations beginning file transfer within 5 seconds of selection
- Report generation processing at least 10,000 backup events per second

### Edge Cases and Error Conditions
- Handling of backup interruptions due to power failure or network issues
- Recovery from corrupted backup repository with minimal data loss
- Proper functioning with extremely large files (e.g., database dumps)
- Correct behavior when storage targets become full during backup operations
- Appropriate error handling for permission issues on protected files
- Graceful handling of conflicting retention policies for multi-category documents

### Required Test Coverage Metrics
- Minimum 90% line coverage for all functional components
- 100% coverage of all public APIs
- All error handling paths must be explicitly tested
- Performance tests must verify all stated benchmarks
- Integration tests must verify all external system interfaces

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
The implementation will be considered successful when:

1. All five key requirements are fully implemented and pass their respective test cases.
2. The system demonstrates the ability to efficiently store incremental backups with proper deduplication.
3. Compliance reports accurately reflect the backup status and retention policy adherence.
4. The cryptographic verification system successfully detects any tampering with backup archives.
5. Role-based access controls properly restrict operations based on assigned permissions.
6. The implementation is well-structured with clean separation of concerns between components.
7. All performance benchmarks are met under the specified load conditions.
8. Code quality meets professional standards with appropriate documentation.

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup
1. Use `uv venv` to setup a virtual environment. From within the project directory, activate it with `source .venv/bin/activate`.
2. Install the project with `uv pip install -e .`
3. CRITICAL: Before submitting, run the tests with pytest-json-report:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```
4. Verify that all tests pass and the pytest_results.json file has been generated.

REMINDER: Generating and providing the pytest_results.json file is a critical requirement for project completion.