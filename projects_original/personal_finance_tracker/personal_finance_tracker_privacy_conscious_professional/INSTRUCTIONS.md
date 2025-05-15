# Secure Financial Tracking System for Privacy-Conscious Professionals

## Overview
A comprehensive personal finance management system specifically designed for privacy-conscious professionals who need to track complex income streams and investments while maintaining complete control over their financial data. This system ensures that all data remains local, encrypted, and never shared with third parties.

## Persona Description
Alex is a technology professional who values data privacy and refuses to use cloud-based financial services that might share or monetize his financial behavior. He needs a comprehensive system to track his complex income streams and investments while maintaining complete control over his financial data.

## Key Requirements
1. **End-to-end encryption for all financial data with local key management**  
   Alex requires military-grade encryption for all financial records, ensuring that even if his device is compromised, his financial data remains protected. The system must support user-managed encryption keys with options for key rotation and secure backup.

2. **Contractor income tracking with project-based categorization and tax withholding calculations**  
   As a technology professional who often works on contract roles alongside full-time employment, Alex needs to track multiple income streams, categorize them by project, client, or role, and automatically calculate appropriate tax withholding amounts for estimated quarterly payments.

3. **Stock option and equity compensation analysis tools for tech industry compensation**  
   Alex's compensation package includes complex equity components like restricted stock units (RSUs), employee stock purchase plans (ESPPs), and stock options with various vesting schedules. He needs specialized tools to track these assets, understand their tax implications, and forecast their potential value under different scenarios.

4. **Financial data isolation ensuring zero external data transmission or telemetry**  
   Given Alex's privacy concerns, the system must guarantee that no financial data is ever transmitted outside the local environment. This requires verification mechanisms to confirm data isolation and options to manually approve any external connections (such as for currency exchange rates).

5. **Self-hosted synchronization between devices without third-party servers**  
   Alex uses multiple devices and needs his financial data to remain synchronized across them without relying on cloud services. The solution must support secure device-to-device synchronization protocols that don't require an intermediary server.

## Technical Requirements
- **Testability Requirements:**
  - All cryptographic functions must be testable with known test vectors
  - Data isolation must be verifiable through network traffic analysis
  - Synchronization protocols must be testable with simulated device connections
  - Test coverage for encryption functions must exceed 95%

- **Performance Expectations:**
  - Encryption/decryption operations must complete in under 500ms for typical financial datasets
  - Local database operations should handle at least 100,000 transactions with query response times under 200ms
  - Synchronization between devices should complete within 60 seconds for typical usage

- **Integration Points:**
  - Secure import of financial data from CSV/QIF/OFX files
  - Optional integration with cryptocurrency wallets via public addresses (no private keys)
  - Support for offline exchange rate data for valuation calculations

- **Key Constraints:**
  - No cloud dependencies whatsoever
  - No telemetry or usage analytics
  - All third-party libraries must be open source and auditable
  - No network access required for core functionality

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must implement these core components:

1. **Secure Data Storage Layer:**
   - Encrypted SQLite database with parameterized queries
   - Key management system with support for key rotation
   - Data integrity verification mechanism

2. **Financial Transaction Engine:**
   - Transaction recording with comprehensive metadata
   - Multiple account management
   - Category and tag system with hierarchical organization
   - Support for recurring transactions and split transactions

3. **Income Analysis System:**
   - Contract/freelance income tracking
   - Project-based income categorization
   - Tax obligation calculator with support for different tax jurisdictions
   - Time-series analysis of income trends

4. **Equity Compensation Tracker:**
   - Stock option grant and exercise modeling
   - RSU tracking with vesting schedules
   - ESPP contribution and purchase tracking
   - Tax basis and capital gains calculations

5. **Secure Synchronization Protocol:**
   - Differential synchronization algorithm
   - Conflict resolution system
   - Encrypted data transfer mechanism
   - Device authentication and authorization

## Testing Requirements
- **Key Functionalities to Verify:**
  - Encryption correctly protects data at rest
  - No data is transmitted externally without explicit permission
  - Tax calculations are accurate for various income scenarios
  - Stock option valuations correctly account for vesting and strike prices
  - Synchronization correctly reconciles changes from multiple devices

- **Critical User Scenarios:**
  - Adding a new contract income source with custom tax withholding
  - Recording stock option grants with complex vesting schedules
  - Performing secure synchronization between two devices
  - Recovering from data corruption using encrypted backups
  - Importing historical financial data from external sources

- **Performance Benchmarks:**
  - Database must handle at least 10 years of daily financial transactions (3,650+ records)
  - Encryption operations must not add more than 50% overhead to database operations
  - Full data backup and restore must complete in under 5 minutes
  - Search and filtering operations must return results in under 1 second

- **Edge Cases and Error Conditions:**
  - Attempted synchronization with unauthorized devices
  - Recovery from corrupted encryption keys
  - Handling of malformed import data
  - Graceful degradation when handling extremely large datasets
  - Maintaining data integrity during interrupted operations

- **Required Test Coverage Metrics:**
  - Overall code coverage: minimum 85%
  - Cryptographic functions: minimum 95%
  - Data synchronization functions: minimum 90%
  - Financial calculation functions: minimum 90%

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
- The system correctly encrypts all financial data with user-managed keys
- Contractor income can be tracked by project with accurate tax withholding calculations
- Stock options and equity compensation can be modeled with proper vesting schedules
- No financial data is ever transmitted externally (verifiable through tests)
- Devices can securely synchronize financial data directly without intermediary servers
- All operations maintain data integrity and security throughout the system
- Performance metrics meet or exceed the specified benchmarks
- All tests demonstrate full functionality without manual intervention

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Environment Setup
1. Set up a virtual environment using `uv venv`
2. Activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`
4. Run tests with:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

REMINDER: Generating and providing the pytest_results.json file is a critical requirement for project completion.