# Financial Transaction Microservices Framework

## Overview
This project is a specialized event-driven microservices framework designed for financial technology applications that require strict data consistency, regulatory compliance, and high transaction throughput. It implements exactly-once delivery semantics, comprehensive audit logging, and circuit breaker patterns to ensure reliable financial transaction processing in a distributed architecture.

## Persona Description
Marcus oversees development at a financial technology company processing thousands of transactions per second. His primary goal is to implement a microservices architecture that maintains strict data consistency while providing the regulatory audit trail required in financial systems.

## Key Requirements

1. **Exactly-once Event Delivery Guarantees with Transaction Idempotence**
   - Implement exactly-once delivery semantics for all financial transaction events
   - Create idempotent transaction handlers to prevent duplicate processing
   - Develop a transaction journal system for event deduplication
   - Include transaction reconciliation mechanisms to verify consistency
   - This feature is critical for financial systems to prevent double-spending or lost transactions

2. **Comprehensive Event Logging with Immutable Audit Capabilities**
   - Create an immutable event log that records all system transactions
   - Implement cryptographic verification of log integrity
   - Support for regulatory compliance requirements (GDPR, PCI DSS, SOX)
   - Include evidence of transaction processing for non-repudiation
   - This feature is essential for financial regulatory compliance and transaction verification

3. **Circuit Breaker Patterns with Progressive Service Degradation**
   - Implement circuit breakers to prevent cascading failures
   - Create fallback mechanisms for critical financial operations
   - Support for progressive service degradation rather than complete outages
   - Include automatic recovery and circuit reset capabilities
   - This feature ensures the system remains operational even during partial failures

4. **Event Sourcing with Compliant Storage Regulations**
   - Implement event sourcing patterns for all financial data
   - Ensure storage mechanisms comply with financial data regulations
   - Support for long-term data retention with integrity guarantees
   - Include data sovereignty controls for multi-regional deployments
   - This feature maintains a complete and compliant history of all financial transactions

5. **Service Authorization Mechanisms with Fine-grained Access Control**
   - Implement service-to-service authentication and authorization
   - Create fine-grained access controls for sensitive financial operations
   - Support for role-based access with principle of least privilege
   - Include audit logging of all access attempts and authorizations
   - This feature ensures that only authorized services can perform sensitive financial operations

## Technical Requirements

### Testability Requirements
- All components must be testable with pytest
- Support for deterministic testing of non-deterministic processes
- Comprehensive testing of failure scenarios and recovery mechanisms
- Simulation of regulatory compliance audits

### Performance Expectations
- Support for processing at least 10,000 financial transactions per second
- Maximum latency of 100ms for critical transaction paths
- Ability to handle spikes of up to 5x normal transaction volume
- Support for consistent performance during partial system degradation

### Integration Points
- Integration with banking and payment processing systems
- Support for financial messaging standards (ISO 20022, SWIFT)
- Compatibility with regulatory reporting systems
- Integration with existing authentication and identity systems

### Key Constraints
- Must maintain data consistency across distributed services
- Must comply with relevant financial regulations
- Must provide cryptographic proof of transaction integrity
- Must operate within defined risk parameters for financial operations

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The framework must provide:

1. **Transaction Processing Engine**
   - Exactly-once processing guarantees
   - Idempotent transaction handlers
   - Transaction reconciliation mechanisms
   - Support for financial transaction types and workflows

2. **Event Sourcing and Audit System**
   - Immutable event log with cryptographic verification
   - Compliant storage with retention policies
   - Event replay capabilities for audit and recovery
   - Non-repudiation mechanisms for all transactions

3. **Resilience and Reliability Infrastructure**
   - Circuit breaker implementation with configurable thresholds
   - Progressive degradation of non-critical services
   - Automatic recovery mechanisms
   - Health monitoring and alerting

4. **Security and Access Control**
   - Service authentication and authorization
   - Fine-grained access control for operations
   - Security audit logging
   - Compliance with financial security standards

5. **System Monitoring and Management**
   - Transaction flow visualization
   - System health monitoring
   - Performance metrics tracking
   - Compliance status reporting

## Testing Requirements

### Key Functionalities that Must be Verified
- Exactly-once delivery semantics under various failure conditions
- Immutability and completeness of the audit log
- Correct operation of circuit breakers and recovery mechanisms
- Compliance with financial data storage regulations
- Effectiveness of service authorization and access control

### Critical User Scenarios
- Processing high volumes of financial transactions
- Handling system component failures gracefully
- Performing regulatory compliance audits
- Recovering from various failure scenarios
- Managing access control for sensitive operations

### Performance Benchmarks
- Sustain 10,000+ transactions per second
- Maintain transaction latency under 100ms at P99
- Process 1M+ events for compliance auditing within 1 hour
- Recovery time objective (RTO) of less than 5 minutes for critical services

### Edge Cases and Error Conditions
- Network partitions between critical services
- Data center outages
- Corrupt or incomplete transaction data
- Authorization system failures
- Extreme transaction volume spikes

### Required Test Coverage Metrics
- Minimum 95% line coverage for all code
- 100% coverage of critical financial transaction paths
- 100% coverage of security and authorization mechanisms
- 100% coverage of failure scenarios and recovery mechanisms

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

1. The system can process financial transactions with exactly-once delivery guarantees
2. All transactions are properly recorded in an immutable audit log
3. The system demonstrates resilience to failures with circuit breaker patterns
4. Storage of financial data complies with regulatory requirements
5. Service-to-service authorization enforces proper access controls
6. Performance meets specified benchmarks under load
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