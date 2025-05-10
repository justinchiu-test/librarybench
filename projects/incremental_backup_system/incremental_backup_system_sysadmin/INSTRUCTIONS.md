# Healthcare-Focused Incremental Backup System

## Overview
A specialized incremental backup system designed for healthcare system administrators to securely back up patient records and critical services. The system prioritizes data integrity, minimal performance impact on production systems, and meets strict healthcare compliance requirements.

## Persona Description
Raj manages servers for a regional healthcare provider that must maintain patient records securely. He needs an automated, reliable backup system that guarantees data integrity and accessibility while minimizing system impact.

## Key Requirements

1. **Application-consistent backup hooks for databases and other stateful services**  
   The system must provide mechanisms to ensure databases and stateful services are in a consistent state during backup. This is critical because healthcare applications require transactional consistency to maintain data integrity, and inconsistent backups could lead to unrecoverable data or compliance violations.

2. **Resource throttling to prevent backup processes from impacting production performance**  
   The backup system needs intelligent resource management to limit CPU, memory, I/O, and network usage during backup operations. This feature is essential because healthcare systems must remain responsive 24/7, and any performance degradation could impact patient care or clinical operations.

3. **Comprehensive error handling with automated retry and escalation procedures**  
   Implement robust error detection, logging, and recovery mechanisms with configurable retry policies and notification escalation. This requirement is vital because backup failures in healthcare environments can lead to data loss that affects patient safety and regulatory compliance.

4. **Multi-tier backup strategy automatically routing data to appropriate storage based on sensitivity**  
   The system must categorize and route different types of healthcare data to appropriate storage tiers with different retention and security policies. This functionality is necessary to balance performance, cost, and compliance requirements across different categories of healthcare data.

5. **Recovery time objective (RTO) testing with simulated restoration drills and performance metrics**  
   Provide capabilities to conduct scheduled recovery testing with timing metrics and validation checks. This feature is crucial because healthcare organizations must verify their ability to restore critical systems within defined time windows to meet business continuity requirements and compliance obligations.

## Technical Requirements

### Testability Requirements
- All components must be testable in isolation with appropriate mocking of external dependencies
- Backup and restore operations must be testable without requiring actual production data
- Performance impact tests must verify resource usage stays within configured limits
- Test fixtures must simulate various database states and service conditions
- Error injection testing must verify recovery mechanisms function correctly

### Performance Expectations
- Backup operations must not decrease application performance by more than 10%
- Database backup hooks must complete transactions within 500ms
- Resource throttling must respond to changing system load within 5 seconds
- System must handle backup repositories of at least 10TB with performance degradation
- Recovery operations must meet configurable RTO targets (typically 15 minutes to 4 hours depending on service)

### Integration Points
- Database connectors for common healthcare database systems (SQL Server, Oracle, PostgreSQL)
- Storage connectors for local, network, and cloud storage systems
- Monitoring system integration for performance and error reporting
- Healthcare application hooks for transaction-consistent backups
- Notification systems for alerts and escalations

### Key Constraints
- Must operate without administrative access to healthcare application internals
- No direct patient data access should be required for system configuration
- All operations must be logged for compliance and audit purposes
- System must function in air-gapped environments when necessary
- Must support operation in regulated healthcare environments (HIPAA, HITECH)

## Core Functionality

The Healthcare-Focused Incremental Backup System must provide the following core functionality:

1. **Intelligent File System Tracking**
   - Monitor file system changes using efficient checksums and change detection
   - Track file modifications, additions, and deletions with minimal overhead
   - Store only changed portions of files (delta encoding) to minimize storage requirements
   - Maintain a catalog of all backup points and their contents for fast reference

2. **Application-Aware Consistency Mechanisms**
   - Coordinate with databases and services to create consistent backup points
   - Support pre and post-backup scripts for application-specific preparation
   - Verify application state consistency before and after backup operations
   - Handle transactional consistency for different database engines

3. **Resource Management**
   - Implement configurable throttling of CPU, memory, I/O, and network usage
   - Provide dynamic throttling that responds to current system load
   - Schedule backups during optimal time windows to minimize impact
   - Support pausing and resuming backup operations when resource contention is detected

4. **Intelligent Data Routing**
   - Classify data according to sensitivity, retention requirements, and access patterns
   - Route different data classes to appropriate storage tiers automatically
   - Apply different compression, encryption, and verification policies based on data classification
   - Support policy-based migration between storage tiers as data ages

5. **Recovery Testing and Verification**
   - Automate recovery testing procedures in isolated environments
   - Measure and report recovery time performance against objectives
   - Verify integrity and consistency of restored data and applications
   - Simulate various failure scenarios to validate recovery procedures

6. **Error Management and Resilience**
   - Implement comprehensive error detection during all backup phases
   - Provide configurable retry policies for different types of failures
   - Support multi-level notification and escalation procedures
   - Create detailed error logs suitable for troubleshooting and compliance

## Testing Requirements

### Key Functionalities to Verify
- Delta-based backup creation and efficient storage utilization
- Application consistency hooks function correctly with simulated database systems
- Resource throttling correctly limits system impact under various conditions
- Multi-tier routing correctly categorizes and stores different data types
- Recovery operations restore data correctly and within time objectives
- Error handling correctly detects, retries, and escalates various failure conditions

### Critical User Scenarios
- Complete system backup with multiple data types and classifications
- Incremental backup after small, medium, and large change sets
- Recovery of specific files, directories, and application data sets
- Recovery of entire systems to meet RTO requirements
- Handling of backup operations during peak system load
- Response to various error conditions (network failure, storage failure, etc.)

### Performance Benchmarks
- Resource utilization must stay below configured thresholds during backup
- Backup speed must achieve at least 100MB/s on standard hardware
- Recovery operations must complete within the configured RTO (specific to each test scenario)
- System must handle at least 1 million files in a single backup repository
- Catalog operations must complete within 1 second for common queries

### Edge Cases and Error Conditions
- Handling of partial backup failures with proper resumption
- Correct behavior when storage destinations become unavailable during backup
- Recovery from corrupted backup repositories or catalog databases
- Handling of extremely large files and directories with many small files
- Proper function with unexpected application states and database conditions

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of error handling and recovery code paths
- All configuration options must be covered by at least one test
- All storage backend implementations must have identical coverage metrics
- All public APIs must have comprehensive integration tests

## Success Criteria

The implementation will be considered successful when it meets the following criteria:

1. **Reliability**
   - Zero data loss during backup and recovery operations in all test scenarios
   - Successful error recovery in at least 95% of simulated failure conditions
   - Corruption detection identifies 100% of intentionally corrupted backup data

2. **Performance Impact**
   - Production system performance impact remains below configured thresholds 
   - Backup and recovery operations meet or exceed speed requirements
   - Resource throttling responds correctly to changing system conditions

3. **Healthcare Compliance**
   - All operations maintain proper audit logs for compliance purposes
   - Data classification and routing correctly handles protected health information (PHI)
   - Encryption and security measures meet relevant healthcare standards

4. **Recovery Capabilities**
   - All recovery tests meet their defined RTO objectives
   - Restored systems and applications function correctly after recovery
   - Point-in-time recovery accurately restores to the selected backup point

5. **Usability for Administrators**
   - API operations follow a consistent and logical pattern
   - Error messages provide actionable information for resolving issues
   - Configuration options have sensible defaults for healthcare environments

## Getting Started

To begin implementing this project:

1. Set up your development environment:
   ```
   uv init --lib
   ```

2. Install the required dependencies:
   ```
   uv sync
   ```

3. Run tests:
   ```
   uv run pytest
   ```

4. Run a specific script:
   ```
   uv run python your_script.py
   ```

The implementation should focus on creating a library with well-defined APIs rather than a user interface application. All functionality should be implemented as classes and functions that can be thoroughly tested with pytest.