# PyMockAPI - Microservices Mesh Mock Server

## Overview
A specialized HTTP API mock server designed for microservices developers to simulate complex service mesh environments. This implementation focuses on mocking multiple interdependent services, service discovery patterns, and distributed system behaviors to enable comprehensive testing of microservices architectures.

## Persona Description
A developer working on microservices who needs to mock multiple interdependent services. She requires service mesh simulation to test complex service interaction patterns and failure cascades.

## Key Requirements

1. **Service dependency graph visualization and simulation**
   - Critical for understanding and testing complex service relationships
   - Enables validation of service communication patterns and dependencies

2. **Circuit breaker behavior emulation with failure thresholds**
   - Essential for testing resilience patterns in distributed systems
   - Allows verification of graceful degradation and recovery mechanisms

3. **Service discovery endpoint mocking with dynamic registration**
   - Vital for testing service registration and discovery workflows
   - Enables validation of dynamic service mesh behaviors

4. **Distributed tracing header propagation and visualization**
   - Required for testing observability implementations
   - Ensures proper trace context propagation across service boundaries

5. **Chaos engineering scenarios for cascade failure testing**
   - Critical for validating system resilience under failure conditions
   - Enables testing of failure isolation and recovery strategies

## Technical Requirements

### Testability Requirements
- All service mesh behaviors must be programmable
- Service dependencies must be dynamically configurable
- Chaos scenarios must be reproducible and deterministic
- Distributed tracing must be verifiable

### Performance Expectations
- Support for 50+ mock services simultaneously
- Service discovery updates within 100ms
- Circuit breaker state changes within 50ms
- Trace header processing with minimal overhead (<5ms)

### Integration Points
- Service registry API for dynamic service management
- Circuit breaker configuration and monitoring APIs
- Distributed tracing context APIs
- Chaos engineering control plane

### Key Constraints
- Implementation must be pure Python with no UI components
- All functionality must be testable via pytest
- Must support standard service mesh protocols
- Should work with common tracing standards (OpenTelemetry, Jaeger)

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The mock server must provide:

1. **Service Dependency Manager**: A system for defining and managing complex service dependency graphs with support for synchronous and asynchronous communication patterns.

2. **Circuit Breaker Engine**: Implementation of circuit breaker patterns with configurable failure thresholds, timeout periods, and half-open states for each service endpoint.

3. **Service Registry**: Dynamic service discovery simulation with registration, deregistration, health checking, and metadata management capabilities.

4. **Distributed Tracing System**: Complete trace context propagation following standards like W3C Trace Context, with span creation and correlation across services.

5. **Chaos Controller**: Controlled failure injection including service outages, network partitions, latency spikes, and cascade failure scenarios.

## Testing Requirements

### Key Functionalities to Verify
- Service dependencies are correctly modeled and enforced
- Circuit breakers transition states appropriately
- Service discovery reflects dynamic changes
- Trace context propagates correctly across services
- Chaos scenarios create expected failure patterns

### Critical User Scenarios
- Testing service communication in complex topologies
- Validating circuit breaker protection mechanisms
- Verifying service discovery during scaling events
- Ensuring trace continuity across service calls
- Testing system resilience to cascade failures

### Performance Benchmarks
- Handle 50+ mock services concurrently
- Service registration/discovery under 100ms
- Circuit breaker decisions under 50ms
- Trace overhead below 5ms per request
- Support 1000+ requests/second across all services

### Edge Cases and Error Conditions
- Circular service dependencies
- Circuit breaker flapping conditions
- Service discovery during network partitions
- Trace context corruption or loss
- Simultaneous failures across multiple services

### Required Test Coverage
- Minimum 90% code coverage for all core modules
- 100% coverage for circuit breaker logic
- Integration tests for service mesh scenarios
- Chaos testing validation
- End-to-end tests for distributed workflows

**IMPORTANT**:
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

1. Complex microservices topologies can be accurately simulated
2. Resilience patterns work correctly under failure conditions
3. Service discovery behaves realistically
4. Distributed tracing provides complete visibility
5. Chaos engineering reveals system weaknesses effectively

**REQUIRED FOR SUCCESS**:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

To set up the development environment:
1. Create a virtual environment using `uv venv` from within the project directory
2. Activate the environment with `source .venv/bin/activate`
3. Install the project in editable mode with `uv pip install -e .`
4. Install test dependencies including pytest-json-report

## Validation

The final implementation must be validated by:
1. Running all tests with pytest-json-report
2. Generating and providing the pytest_results.json file
3. Demonstrating all five key requirements are fully implemented
4. Showing effective microservices testing capabilities

**CRITICAL**: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion.