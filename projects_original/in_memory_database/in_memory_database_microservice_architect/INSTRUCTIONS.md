# ResilioStore: Distributed In-Memory Database for Microservices

## Overview
A specialized in-memory database designed for distributed microservice architectures that provides resilient local data storage, event sourcing capabilities, configurable consistency models, failure-handling patterns, and schema management functions to ensure system reliability during network partitions while supporting eventual data synchronization.

## Persona Description
Anika designs distributed systems using microservices architecture. She needs local data storage for services that remains performant during network partitions while eventually synchronizing with other services.

## Key Requirements

1. **Event Sourcing for State Reconciliation**
   - Implementation of an event sourcing system that preserves all state transitions
   - Support for event replay and reconstruction of state from event history
   - Mechanisms for conflict resolution during eventual reconciliation
   - This feature is critical for Anika's microservice architecture as it provides a reliable foundation for state synchronization after network partitions, ensuring that distributed services can reconstruct a consistent view of data once connectivity is restored

2. **Configurable Consistency Models**
   - Implementation of multiple consistency models with explicit trade-offs between consistency and availability
   - Support for tunable consistency levels for different data types and operations
   - Clear documentation of consistency guarantees for each model
   - Microservice architectures require different consistency models for different data types and operations, allowing Anika to make appropriate trade-offs between consistency, availability, and performance based on business requirements

3. **Circuit Breaker Pattern Implementation**
   - Implementation of circuit breaker patterns for detecting and responding to downstream service failures
   - Configurable failure thresholds and recovery strategies
   - Support for fallback behaviors during open circuit conditions
   - When connections between microservices fail, circuit breakers prevent cascading failures and resource exhaustion, allowing Anika's services to degrade gracefully and recover automatically when conditions improve

4. **Service Mesh Integration**
   - Implementation of integration points with service mesh technologies for coordinated distributed transactions
   - Support for distributed tracing contexts
   - Compatibility with common service mesh communication patterns
   - Service meshes have become a standard approach for managing microservice communication, and integration allows Anika to coordinate database operations with broader service interactions and observability

5. **Schema Registry Integration**
   - Implementation of schema versioning and compatibility enforcement
   - Support for schema evolution while maintaining backward compatibility
   - Integration with external schema registries for coordinated schema management
   - As microservices evolve independently, schema management becomes critical for ensuring that data remains interoperable across services, preventing data corruption or misinterpretation during service interactions

## Technical Requirements

### Testability Requirements
- Event sourcing must be testable with various concurrency scenarios
- Different consistency models must have verifiable behavior under partition conditions
- Circuit breaker implementations must be testable with simulated failures
- Service mesh integration must be verifiable through standardized interfaces
- Schema compatibility must be testable across version changes

### Performance Expectations
- Local operations must complete in under 5ms at p99
- Event sourcing overhead should not exceed 10% of base operation time
- System should handle at least 10,000 operations per second per service instance
- Recovery after partition should process at least 1,000 events per second
- Schema validation should add no more than 1ms overhead per operation

### Integration Points
- Interfaces for common service mesh implementations
- Compatible APIs for distributed tracing systems
- Integration with standard schema registry implementations
- Support for health check and readiness probe protocols
- Interfaces for monitoring and observability platforms

### Key Constraints
- The implementation must use only Python standard library with no external dependencies
- The system must operate efficiently within typical microservice resource allocations
- All functionality must be resilient to unexpected process termination
- The solution must maintain performance under partial failure conditions

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide the following core functionality:

1. **Local Data Store**
   - Efficient in-memory storage for service-local data
   - ACID-compliant transaction support
   - Query capabilities optimized for microservice data access patterns

2. **Event Sourcing System**
   - Event capture and storage for all state-changing operations
   - Event replay capabilities for state reconstruction
   - Conflict detection and resolution mechanisms

3. **Consistency Management**
   - Implementation of various consistency models
   - Explicit control over consistency-availability trade-offs
   - Monitoring of consistency state and potential conflicts

4. **Resilience Patterns**
   - Circuit breaker implementation for external dependencies
   - Backoff strategies for retry operations
   - Graceful degradation under failure conditions

5. **Schema Management**
   - Schema versioning and compatibility checking
   - Support for schema evolution with backward compatibility
   - Integration with external schema registries

## Testing Requirements

### Key Functionalities to Verify
- Correct local data operations with transactional integrity
- Accurate event sourcing with proper reconstruction of state
- Behavior of different consistency models under network partitions
- Effective operation of circuit breakers during service failures
- Proper handling of schema evolution and compatibility

### Critical User Scenarios
- Normal operation with fully connected services
- Continued operation during network partition
- Recovery and reconciliation after partition healing
- Graceful degradation when downstream services fail
- Schema evolution while maintaining compatibility

### Performance Benchmarks
- Local read operations must complete in under 2ms at p99
- Local write operations must complete in under 5ms at p99
- Event sourcing overhead should not exceed 10% of base operation time
- Each service instance should handle at least 10,000 operations per second
- State reconstruction from events should process at least 1,000 events per second

### Edge Cases and Error Conditions
- Behavior during prolonged network partitions
- Recovery from process crashes during transaction processing
- Handling of incompatible schema changes
- Operation under extreme memory pressure
- Performance with large accumulated event histories

### Required Test Coverage Metrics
- Minimum 90% code coverage for all modules
- 100% coverage of conflict resolution and event sourcing code
- All error recovery paths must be tested
- Performance tests must cover normal and degraded conditions
- Resilience tests must verify behavior under various failure scenarios

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

1. Services maintain local data accessibility during network partitions
2. Event sourcing enables accurate state reconciliation after connectivity is restored
3. Consistency models provide appropriate trade-offs for different operational requirements
4. Circuit breakers effectively prevent cascading failures
5. Schema management ensures compatibility across service versions

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup

To set up the development environment:

1. Clone the repository and navigate to the project directory
2. Create a virtual environment using:
   ```
   uv venv
   ```
3. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```
4. Install the project in development mode:
   ```
   uv pip install -e .
   ```
5. Run tests with:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

CRITICAL REMINDER: Generating and providing the pytest_results.json file is a MANDATORY requirement for project completion.