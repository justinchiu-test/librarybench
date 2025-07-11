# PyMockAPI - IoT Device Mock Server

## Overview
A specialized HTTP API mock server designed for IoT developers to simulate device communication endpoints and protocols. This implementation focuses on lightweight mocking for resource-constrained environments, supporting both HTTP/REST and IoT-specific protocols like MQTT, enabling comprehensive testing of IoT device interactions.

## Persona Description
An IoT developer testing device communication who needs to simulate various device endpoints and protocols. He requires lightweight mocking for resource-constrained environments and specific IoT protocols.

## Key Requirements

1. **MQTT endpoint simulation alongside HTTP/REST**
   - Essential for testing IoT devices that use MQTT for efficient communication
   - Enables validation of publish/subscribe patterns and QoS levels

2. **Device fleet simulation with unique device identities**
   - Critical for testing scalable device management solutions
   - Allows validation of device provisioning and identity management

3. **Telemetry data streaming with realistic sensor patterns**
   - Vital for testing data ingestion pipelines and analytics
   - Enables simulation of various sensor types and data patterns

4. **Command acknowledgment patterns for device control**
   - Required for testing device control and actuation workflows
   - Ensures proper handling of command delivery and confirmation

5. **Edge computing scenario simulation with local processing**
   - Essential for testing edge/fog computing architectures
   - Enables validation of local decision-making and data filtering

## Technical Requirements

### Testability Requirements
- All IoT protocols must be mockable via Python APIs
- Device simulations must be scriptable and deterministic
- Telemetry patterns must be configurable and verifiable
- Edge computing scenarios must be reproducible

### Performance Expectations
- Support for 1000+ simulated IoT devices
- MQTT message handling at 10,000 messages/second
- Telemetry generation with minimal resource usage
- Sub-second command acknowledgment latency

### Integration Points
- HTTP REST API for device management
- MQTT broker interface for pub/sub operations
- Telemetry data export APIs
- Device provisioning and identity APIs

### Key Constraints
- Implementation must be pure Python with no UI components
- All functionality must be testable via pytest
- Must be lightweight enough for resource-constrained testing
- Should support standard IoT protocols and patterns

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The mock server must provide:

1. **Multi-Protocol Server**: Unified server supporting both HTTP/REST endpoints and MQTT broker functionality with configurable topics, QoS levels, and retained messages.

2. **Device Fleet Manager**: System for simulating large numbers of IoT devices with unique identities, capabilities, metadata, and lifecycle states.

3. **Telemetry Generator**: Configurable data generators for various sensor types (temperature, humidity, motion, etc.) with realistic patterns and anomalies.

4. **Command Processing Engine**: Bidirectional communication system for device commands with acknowledgment patterns, retry logic, and timeout handling.

5. **Edge Computing Simulator**: Local processing simulation including data aggregation, filtering, edge analytics, and selective cloud synchronization.

## Testing Requirements

### Key Functionalities to Verify
- MQTT and HTTP protocols work correctly together
- Device fleet scales to required numbers
- Telemetry data follows realistic patterns
- Commands are delivered and acknowledged properly
- Edge computing logic executes as configured

### Critical User Scenarios
- Provisioning and onboarding new IoT devices
- Streaming telemetry from multiple sensors
- Sending commands to device fleets
- Testing MQTT QoS and retention policies
- Simulating edge processing and filtering

### Performance Benchmarks
- Simulate 1000+ IoT devices concurrently
- Process 10,000 MQTT messages per second
- Generate telemetry with <1% CPU per device
- Command acknowledgment within 1 second
- Edge processing latency under 100ms

### Edge Cases and Error Conditions
- Handling intermittent device connectivity
- MQTT broker connection failures
- Telemetry data overflow conditions
- Command delivery to offline devices
- Edge node resource exhaustion

### Required Test Coverage
- Minimum 90% code coverage for all core modules
- 100% coverage for protocol implementations
- Integration tests for IoT scenarios
- Load tests for device scaling
- Protocol compliance tests

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

1. Both HTTP and MQTT protocols are fully supported
2. Large device fleets can be realistically simulated
3. Telemetry patterns match real-world sensor behavior
4. Bidirectional communication works reliably
5. Edge computing scenarios are accurately modeled

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
4. Showing effective IoT device simulation capabilities

**CRITICAL**: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion.