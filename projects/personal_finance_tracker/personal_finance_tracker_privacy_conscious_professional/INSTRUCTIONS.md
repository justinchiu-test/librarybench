# Privacy-First Financial Management System

A personal finance tracker focused on data privacy, security, and complete user control for technology professionals with complex income streams.

## Overview

This library provides a comprehensive financial tracking and management system designed specifically for privacy-conscious technology professionals. It focuses on local data storage with strong encryption, specialized tracking for tech industry compensation, and eliminates any external data sharing while allowing secure device synchronization.

## Persona Description

Alex is a technology professional who values data privacy and refuses to use cloud-based financial services that might share or monetize his financial behavior. He needs a comprehensive system to track his complex income streams and investments while maintaining complete control over his financial data.

## Key Requirements

1. **End-to-end encryption for all financial data with local key management**
   - All financial data must be encrypted using strong cryptographic standards
   - Users need complete control over encryption keys with secure key management
   - Data should be encrypted at rest with no plaintext storage of sensitive information
   - This feature is critical as it ensures the user's financial information remains private even if the storage medium is compromised

2. **Contractor income tracking with project-based categorization and tax withholding calculations**
   - Support for tracking multiple contract jobs simultaneously with clear project separation
   - Automated tax withholding calculations based on contract type and jurisdiction
   - Income categorization by client, project, and income type for detailed reporting
   - This feature is essential for tech professionals who often balance full-time work with consulting or contract projects

3. **Stock option and equity compensation analysis tools for tech industry compensation**
   - Track various equity compensation types (RSUs, ISOs, NSOs, ESPPs)
   - Calculate vesting schedules and projected values based on grant dates
   - Estimate tax implications for different equity exercise scenarios
   - This feature addresses the complexity of tech industry compensation packages that often include significant equity components

4. **Financial data isolation ensuring zero external data transmission or telemetry**
   - No network capabilities or external API calls within core financial functionality
   - Verification mechanisms to ensure data remains local
   - Clear logging of any file system operations for transparency
   - This requirement is fundamental for users who prioritize data privacy above convenience features requiring external connectivity

5. **Self-hosted synchronization between devices without third-party servers**
   - Secure data export/import functionality with versioning
   - Conflict resolution for changes made on different devices
   - Optional local network synchronization without internet dependency
   - This feature ensures users can access their financial data across devices without compromising on their privacy requirements

## Technical Requirements

### Testability Requirements
- All modules must have comprehensive unit tests with ≥90% code coverage
- Encryption and security features must have both unit and integration tests
- Mock implementations for all external dependencies (file system, time, etc.)
- Test suites must run without any external network access

### Performance Expectations
- Database operations should remain responsive with up to 10 years of daily transaction data (est. ~50,000 transactions)
- Encryption/decryption operations should not introduce noticeable latency (< 100ms)
- Complete data export/backup operations should complete in < 30 seconds
- Analysis and reporting features should generate results in < 5 seconds

### Integration Points
- Secure file import/export functionality for CSV, QIF, OFX financial data
- Local filesystem integration for backup and data persistence
- Optional local network socket for device synchronization

### Key Constraints
- Zero external API dependencies or network calls for core functionality
- No cloud services or third-party analytics
- All cryptographic implementations must use well-established libraries rather than custom implementations
- Data format must be open and documented to prevent vendor lock-in

## Core Functionality

The system must provide these core components:

1. **Secure Data Storage Layer**: 
   - Encrypted SQLite database with separation between metadata and sensitive data
   - Key management system allowing secure key rotation and backup
   - Transaction journaling to prevent data corruption

2. **Financial Management Core**:
   - Double-entry accounting system for transaction tracking
   - Transaction categorization with custom taxonomy support
   - Budget management with variance tracking
   - Multi-currency support with exchange rate tracking

3. **Tech Compensation Tracking**:
   - Equity grant management (options, RSUs, etc.)
   - Vesting schedule tracking
   - Exercise planning and tax implication modeling
   - Compensation package comparison tools

4. **Contract Work Management**:
   - Project and client organization
   - Time tracking integration
   - Invoice and payment tracking
   - Automated tax withholding calculations

5. **Privacy-Focused Synchronization**:
   - Encrypted data export format
   - Versioning and conflict resolution
   - Incremental sync to minimize transfer size
   - Local network discovery and direct device-to-device transfer

## Testing Requirements

### Key Functionalities to Verify
- Proper encryption/decryption of all sensitive financial data
- Accurate calculation of tax withholding for various contractor scenarios
- Correct tracking and valuation of different equity compensation types
- Data integrity through synchronization scenarios
- Complete isolation from external networks during operation

### Critical User Scenarios
- Setting up the system with a new encryption key
- Importing historical financial data from CSV exports
- Tracking a complex compensation package (salary + bonuses + equity)
- Managing multiple simultaneous contract jobs with different payment terms
- Synchronizing data between multiple devices securely

### Performance Benchmarks
- Database performance with 10+ years of financial data (≥50,000 transactions)
- Memory usage under 200MB during normal operation
- CPU utilization <10% during idle monitoring
- Sub-second response time for common queries and reports

### Edge Cases and Error Conditions
- Recovery from corrupt database files
- Handling of interrupted synchronization
- Encryption key backup and recovery processes
- Graceful handling of malformed import data
- Timezone handling for transactions across different regions

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of security-critical components
- Integration tests for all user-facing features
- Performance tests for database operations with large datasets

## Success Criteria

The implementation will be considered successful when:

1. All financial data is securely encrypted with no plaintext storage of sensitive information
2. Users can track and categorize income from multiple technology industry sources including contract work and equity compensation
3. The system operates with zero external data transmission as verified by network monitoring
4. Users can successfully synchronize financial data between multiple devices without third-party servers
5. Tax withholding calculations for contractors are accurate within 0.1% of manually verified calculations
6. Equity compensation tracking correctly handles complex vesting schedules and valuation changes
7. All operations remain responsive with datasets containing 10+ years of financial history
8. 100% of tests pass, including security, performance, and functional test suites

## Getting Started

To set up the development environment:

```bash
cd /path/to/project
uv init --lib
```

This will create a virtual environment and generate a `pyproject.toml` file. To install dependencies:

```bash
uv sync
```

To run individual Python scripts:

```bash
uv run python script.py
```

To run tests:

```bash
uv run pytest
```

The implementation should prioritize standard library components for core functionality but may use:
- `pydantic` for data validation
- `cryptography` for encryption functionality
- `pytest` for testing