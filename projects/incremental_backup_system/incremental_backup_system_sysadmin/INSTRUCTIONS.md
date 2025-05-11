# MedBackup - Enterprise Incremental Backup System for Healthcare

## Overview
A specialized incremental backup system designed for system administrators managing healthcare servers. The system enables application-consistent backups of critical databases and patient records, with robust error handling, fine-grained resource control, and comprehensive compliance features to meet regulatory requirements while minimizing performance impact on production systems.

## Persona Description
Raj manages servers for a regional healthcare provider that must maintain patient records securely. He needs an automated, reliable backup system that guarantees data integrity and accessibility while minimizing system impact.

## Key Requirements
1. **Application-consistent Backup Hooks**: Implement a flexible framework for pre- and post-backup operations that ensures databases and stateful services are backed up in consistent states. This capability allows Raj to create reliable backups of critical healthcare applications without service interruption, ensuring that restored data will be internally consistent and usable.

2. **Resource Throttling System**: Develop sophisticated resource control mechanisms that limit CPU, memory, network, and I/O usage during backup operations. This feature enables Raj to prevent backup processes from impacting the performance of production healthcare systems serving patients and medical staff, maintaining service quality while still ensuring comprehensive data protection.

3. **Comprehensive Error Recovery**: Create an advanced error handling system with automated retry logic, failure isolation, and administrative escalation procedures. This resilient approach ensures that backups complete successfully even in the face of transient issues, with clear alerting when human intervention is required to address persistent problems.

4. **Multi-tier Backup Strategy**: Implement policy-based data routing that automatically directs different types of healthcare data to appropriate storage systems based on sensitivity, retention requirements, and access patterns. This capability allows Raj to optimize storage costs while ensuring that sensitive patient data receives appropriate protection levels.

5. **Recovery Time Objective Testing**: Develop functionality for simulating and measuring restoration operations without affecting production systems. This feature enables Raj to validate that backup sets can be restored within required timeframes and perform regular recovery drills to ensure the organization can meet its business continuity obligations.

## Technical Requirements

### Testability Requirements
- All components must have isolated unit tests with dependency injection for external systems
- Application consistency hooks must be tested with simulated database states
- Resource throttling must be verifiable across various system constraints
- Error handling must be tested with comprehensive failure injection
- Multi-tier routing must be validated with policy-driven test scenarios
- RTO testing must measure performance against defined recovery benchmarks

### Performance Expectations
- The system must efficiently handle backup sets up to 100TB in size
- Application consistency operations must add less than 30 seconds per application
- Resource usage must stay within configured limits with 99.9% accuracy
- Error recovery must resolve at least 95% of common failure scenarios without intervention
- Policy-based routing must process at least 100 files per second with correct classification
- RTO simulation must predict actual recovery times with ±10% accuracy

### Integration Points
- Database management systems (Oracle, SQL Server, PostgreSQL, MongoDB)
- Healthcare application APIs (Epic, Cerner, Meditech, etc.)
- Enterprise storage systems and hierarchical storage management
- System monitoring and alerting infrastructure
- Compliance and audit logging systems
- Bare metal recovery and virtualization platforms

### Key Constraints
- The implementation must work on enterprise Linux distributions
- All operations must comply with HIPAA and other healthcare regulations
- The system must accommodate both virtual and physical server environments
- Storage formats must support encryption and access controls
- Performance impact must be strictly controllable within administrator-defined limits
- System must provide complete audit trails for all backup and restoration operations

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core of this implementation centers on a Python library that provides:

1. **Incremental Backup Engine**: A core module handling efficient delta storage with block-level deduplication and compression, optimized for healthcare data patterns and regulatory compliance.

2. **Application Integration Framework**: Extensible hooks for connecting with databases and healthcare applications to create consistent backups without service interruption or data corruption.

3. **Resource Management Controller**: Sophisticated throttling and scheduling functionality that limits backup impact on production systems using dynamic resource monitoring and adaptation.

4. **Error Handling Orchestrator**: Comprehensive error detection, classification, recovery, and escalation capabilities that maximize backup completion rates while providing clear remediation paths.

5. **Policy Enforcement System**: Rules-based routing and retention management that applies appropriate storage tiers, encryption, and protection levels based on data classification.

6. **Recovery Simulation Environment**: Tools for modeling and measuring restoration performance using isolated testing environments that validate recoverability and timing objectives.

The system should be designed as a collection of Python modules with clear interfaces between components, allowing them to be used independently or as an integrated solution. All functionality should be accessible through a programmatic API that could be called by various management tools (though implementing a UI is not part of this project).

## Testing Requirements

### Key Functionalities to Verify
- Application consistency with proper pre- and post-backup procedures
- Resource throttling with accurate enforcement of configured limits
- Error recovery with correct handling of various failure scenarios
- Policy-based routing with appropriate data classification and tier assignment
- Recovery time prediction with accurate performance measurement
- Comprehensive audit logging with complete operation tracking

### Critical User Scenarios
- Full enterprise backup cycle from scheduling through completion to verification
- Database backup with zero application downtime or corruption
- Dynamic throttling during high-load periods on production systems
- Automated recovery from common failure conditions without data loss
- Compliance reporting for healthcare regulatory requirements
- Disaster recovery simulation with accurate RTO measurement

### Performance Benchmarks
- Initial full backup processing at least 50MB/s per thread
- Incremental backups identifying changes within 5% of optimal theoretical time
- Resource throttling responding to threshold changes within 10 seconds
- Error recovery initiating retry sequences within a 5-second window
- Backup classification and routing deciding correct tier in under 50ms per file
- Recovery simulation predicting completion times within 10% of actual durations

### Edge Cases and Error Conditions
- Handling of database transactions in progress during backup initiation
- Recovery from storage subsystem failures during backup operations
- Proper functioning during server failover or clustering events
- Correct behavior when primary backup targets become unavailable
- Appropriate handling of application API failures or timeouts
- Graceful operation during resource constraint violations

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
2. The system demonstrates application-consistent backups for at least one database type.
3. Resource throttling effectively limits system impact according to configured constraints.
4. Error handling successfully recovers from common failure scenarios automatically.
5. Policy-based routing correctly assigns data to appropriate tiers based on classification.
6. Recovery time simulation provides accurate estimates of restoration performance.
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