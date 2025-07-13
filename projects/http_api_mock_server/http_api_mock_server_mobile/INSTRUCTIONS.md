# PyMockAPI - Mobile Network Condition Simulator

## Overview
A specialized HTTP API mock server designed for mobile app developers to test application behavior under various network conditions. This implementation focuses on simulating realistic mobile network scenarios including unstable connectivity, packet loss, and offline-to-online transitions to ensure robust mobile app development.

## Persona Description
A mobile developer creating a offline-first app who needs to test various network conditions and API failures. He wants to simulate unreliable network scenarios to ensure the app handles connectivity issues gracefully.

## Key Requirements

1. **Network condition simulation with packet loss and jitter**
   - Critical for testing how mobile apps handle unreliable cellular networks and WiFi connections
   - Enables validation of retry logic and error handling in real-world network conditions

2. **Progressive response degradation for offline-to-online transitions**
   - Essential for testing offline-first architectures and sync mechanisms
   - Allows developers to verify data consistency during network state changes

3. **Mobile-specific headers and user agent detection**
   - Required for testing platform-specific API behaviors and responses
   - Enables proper handling of iOS/Android specific requirements

4. **Push notification endpoint simulation with delivery callbacks**
   - Vital for testing push notification workflows without actual device deployment
   - Allows verification of notification handling and delivery confirmation logic

5. **Bandwidth throttling with chunked response streaming**
   - Critical for testing app performance on slow connections (2G/3G/4G)
   - Enables optimization of data usage and loading strategies

## Technical Requirements

### Testability Requirements
- All network simulation features must be controllable via Python APIs
- Mock server must support programmatic configuration changes during test execution
- Response timing and network conditions must be deterministic for test repeatability
- Support for concurrent testing with isolated mock instances

### Performance Expectations
- Must handle at least 100 concurrent connections to simulate multiple app instances
- Network condition changes must take effect within 100ms
- Response streaming must accurately simulate specified bandwidth limits
- Memory usage must remain stable during long-running tests

### Integration Points
- RESTful API for configuring network conditions and mock responses
- Webhook support for push notification delivery callbacks
- Metrics API for monitoring simulated network conditions
- Configuration file support for predefined network scenarios

### Key Constraints
- Implementation must be pure Python with no UI components
- All functionality must be testable via pytest
- Must not require root/admin privileges for network simulation
- Should work cross-platform (Linux, macOS, Windows)

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The mock server must provide:

1. **Network Condition Engine**: A configurable system that can simulate various mobile network conditions including latency, packet loss, jitter, and bandwidth limitations at the application level.

2. **Response Degradation System**: Progressive response quality reduction that simulates the transition from offline to online states, including partial data delivery and connection interruptions.

3. **Mobile Context Detector**: Automatic detection and response customization based on mobile-specific headers, user agents, and device characteristics.

4. **Push Notification Simulator**: Complete push notification workflow simulation including endpoint registration, message delivery, and callback mechanisms.

5. **Bandwidth Control**: Accurate bandwidth throttling with support for chunked transfer encoding to simulate slow mobile connections.

## Testing Requirements

### Key Functionalities to Verify
- Network condition simulation accurately reflects configured parameters
- Progressive degradation follows expected patterns during state transitions
- Mobile-specific responses are correctly triggered by appropriate headers
- Push notification delivery follows expected workflow with proper callbacks
- Bandwidth throttling accurately limits data transfer rates

### Critical User Scenarios
- Mobile app losing and regaining connectivity during data sync
- Push notification delivery under various network conditions
- Large file downloads over throttled connections
- API calls with high latency and packet loss
- Offline queue processing when connection is restored

### Performance Benchmarks
- Network condition changes applied within 100ms
- Support for 100+ concurrent connections
- Bandwidth throttling accuracy within 5% of target rate
- Memory usage stable over 1000+ request/response cycles
- Push notification delivery latency under 500ms

### Edge Cases and Error Conditions
- Handling of malformed mobile headers
- Recovery from simulated total network failure
- Concurrent modification of network conditions
- Push notification delivery to non-existent endpoints
- Bandwidth throttling with very large responses

### Required Test Coverage
- Minimum 90% code coverage for all core modules
- 100% coverage for network simulation logic
- Integration tests for all mobile-specific features
- Performance tests for concurrent connection handling
- Stress tests for memory stability

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

1. All network simulation features work as specified and are fully testable
2. Mobile app developers can effectively test offline-first architectures
3. Push notification workflows can be completely simulated and tested
4. Network conditions can be changed dynamically during test execution
5. Performance meets or exceeds all specified benchmarks

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
4. Showing stable performance under concurrent load

**CRITICAL**: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion.