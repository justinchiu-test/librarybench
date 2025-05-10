# Financial Transaction Microservices Framework

## Overview
A high-integrity microservices framework designed for financial systems processing thousands of transactions per second with strict data consistency and comprehensive regulatory audit capabilities. This framework ensures transaction reliability, provides extensive audit trails, and implements sophisticated fault tolerance while maintaining regulatory compliance.

## Persona Description
Marcus oversees development at a financial technology company processing thousands of transactions per second. His primary goal is to implement a microservices architecture that maintains strict data consistency while providing the regulatory audit trail required in financial systems.

## Key Requirements

1. **Exactly-once Event Delivery Guarantees with Transaction Idempotence**
   - Implement reliable event delivery mechanisms with deduplication and idempotence handling
   - Create transaction idempotency keys and detection mechanisms across services
   - This feature is critical for Marcus as it prevents duplicate transactions that could lead to financial losses, regulatory violations, and damage to the company's reputation, ensuring each financial transaction is processed exactly once

2. **Comprehensive Event Logging with Immutable Audit Capabilities**
   - Develop a tamper-proof event logging system with cryptographic verification
   - Create structured audit trails that capture all transaction details and processing history
   - This capability provides Marcus with the immutable record-keeping required by financial regulations, enabling proof of compliance during audits and investigations into transaction disputes

3. **Circuit Breaker Patterns with Progressive Service Degradation**
   - Implement adaptive circuit breakers that detect failure patterns across services
   - Create configurable degradation strategies that maintain core financial functions during partial outages
   - This feature enables Marcus's system to maintain essential financial services during disruptions, preventing complete system outages while protecting data integrity

4. **Event Sourcing with Compliant Storage Regulations for Financial Data**
   - Develop an event sourcing pattern that maintains the complete history of all financial transactions
   - Implement regulatory-compliant storage with appropriate retention, encryption, and access controls
   - This capability ensures Marcus's systems maintain a legally compliant record of all financial activities while enabling reconstruction of any account state at any point in time

5. **Service Authorization Mechanisms with Fine-grained Access Control**
   - Implement service-to-service authentication with strong identity verification
   - Create role-based access controls at the operation and data field levels
   - This feature protects sensitive financial data and operations by ensuring only authorized services can perform specific actions, meeting regulatory requirements for data protection and access control

## Technical Requirements

### Testability Requirements
- All transaction processing flows must be testable with controlled input and verification
- Audit logging must be verifiable for completeness and tamper resistance
- Circuit breaker behaviors must be testable through simulated failure scenarios
- Event sourcing must be validated for data consistency and reconstruction accuracy
- Authorization mechanisms must be thoroughly testable for security vulnerabilities

### Performance Expectations
- Transaction processing must handle sustained rates of 5,000 TPS with peaks of 10,000 TPS
- Event logging must occur synchronously with transaction processing with minimal latency impact
- Circuit breakers must detect failures within 500ms and react within 1 second
- Event sourcing must support state reconstruction at a rate of at least 1,000 events per second
- Authorization checks must add no more than 10ms overhead per service call

### Integration Points
- Integration with financial messaging systems (ISO 20022, FIX, etc.)
- Hooks for regulatory reporting systems (AML, fraud detection, etc.)
- Interfaces for external audit systems
- Adapters for payments networks and settlement systems
- Integration with identity and access management systems

### Key Constraints
- Must comply with relevant financial regulations (PCI DSS, SOX, etc.)
- Must maintain transaction atomicity across distributed services
- No data loss is acceptable under any circumstances
- Must support disaster recovery with minimal data reconciliation
- Must operate with strict audit trails for all system changes

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The framework must provide the following core functionality:

1. **Financial Transaction Processing**
   - Exactly-once delivery semantics for financial events
   - Transaction idempotence mechanisms
   - Distributed transaction coordination

2. **Regulatory Compliance System**
   - Immutable audit trail with cryptographic verification
   - Compliance metadata attachment to transactions
   - Retention policy enforcement

3. **Resilience Framework**
   - Circuit breaker implementation with configurable policies
   - Service degradation strategies
   - Recovery coordination

4. **Event Sourcing Infrastructure**
   - Append-only event storage with compliance features
   - State reconstruction from event streams
   - Temporal querying capabilities

5. **Access Control System**
   - Service-to-service authentication
   - Fine-grained authorization policies
   - Audit logging of access attempts

6. **Financial Data Integrity**
   - Data validation and consistency checking
   - Reconciliation mechanisms
   - Data lineage tracking

## Testing Requirements

### Key Functionalities That Must Be Verified
- Exactly-once processing guarantees are maintained under all conditions
- Audit trails are complete, accurate, and tamper-resistant
- Circuit breakers correctly detect failures and apply appropriate degradation
- Event sourcing accurately reconstructs system state
- Access controls properly restrict operations based on service identity and permissions

### Critical User Scenarios
- High-volume financial transaction processing with no duplicates or losses
- Regulatory audit of transaction history spanning multiple services
- Graceful degradation during partial system failure
- Full system reconstruction from event history
- Service-to-service communication with proper authentication and authorization

### Performance Benchmarks
- Sustained transaction processing at required throughput levels
- Audit logging with minimal latency impact
- Circuit breaker response within defined timeframes
- Event sourcing reconstruction performance
- Authorization system throughput under peak load

### Edge Cases and Error Conditions
- Network partitions during transaction processing
- Partial failures in distributed transactions
- Recovery from total system failure
- Attempted tampering with audit logs
- Authentication system outages

### Required Test Coverage Metrics
- 100% coverage of transaction processing logic
- 100% coverage of audit logging mechanisms
- 100% coverage of circuit breaker implementations
- 100% coverage of event sourcing reconstruction
- 100% coverage of authentication and authorization logic

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
- Zero financial transactions lost or duplicated
- Full compliance with regulatory audit requirements
- System maintains critical functions during partial failures
- Any point-in-time state can be accurately reconstructed
- No unauthorized operations succeed even under failure conditions
- System handles peak transaction loads with consistent performance
- All regulatory reports can be generated from stored event data
- Financial reconciliation balanced to the penny across all services

## Getting Started

To set up the development environment for this project:

1. Initialize the project using `uv`:
   ```
   uv init --lib
   ```

2. Install dependencies using `uv sync`

3. Run tests using `uv run pytest`

4. To execute specific Python scripts:
   ```
   uv run python your_script.py
   ```

5. For running linters and type checking:
   ```
   uv run ruff check .
   uv run pyright
   ```

Remember to design the framework as a library with well-documented APIs, not as an application with user interfaces. All functionality should be exposed through programmatic interfaces that can be easily tested and integrated into larger systems.