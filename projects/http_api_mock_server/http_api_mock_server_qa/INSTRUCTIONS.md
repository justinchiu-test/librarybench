# PyMockAPI - Test Automation Mock Server

## Overview
A specialized HTTP API mock server designed for QA automation engineers to create deterministic, controllable test environments. This implementation focuses on providing programmatic control over mock responses, test isolation, and seamless integration with automated testing frameworks to ensure reliable and repeatable test execution.

## Persona Description
A QA engineer building end-to-end test suites who needs deterministic API responses for test reliability. She requires the ability to programmatically control mock responses during test execution to validate different application states.

## Key Requirements

1. **Test harness API for runtime mock configuration**
   - Essential for dynamically controlling mock behavior during test execution
   - Enables test scenarios to modify responses without restarting the mock server

2. **Deterministic sequence playback for multi-step test scenarios**
   - Critical for testing complex workflows with predictable state transitions
   - Ensures test repeatability across different environments and executions

3. **Response assertion recording for automated verification**
   - Vital for validating that applications make expected API calls
   - Enables comprehensive testing of request parameters and sequences

4. **Test isolation with namespace-based mock separation**
   - Required for running parallel tests without interference
   - Ensures each test suite has its own isolated mock environment

5. **Cucumber/BDD integration with scenario tag mapping**
   - Essential for mapping test scenarios to specific mock configurations
   - Enables behavior-driven testing with clear mock state definitions

## Technical Requirements

### Testability Requirements
- Mock server must expose a control API for test frameworks
- All configuration changes must be atomic and immediately effective
- Response sequences must be perfectly repeatable
- Support for resetting mock state between test runs

### Performance Expectations
- Configuration changes must take effect within 50ms
- Support for at least 50 concurrent isolated test namespaces
- Response assertion queries must return within 10ms
- Mock state reset must complete within 100ms

### Integration Points
- RESTful control API for test harness integration
- WebSocket API for real-time assertion notifications
- File-based configuration for initial mock setup
- Export API for test result correlation

### Key Constraints
- Implementation must be pure Python with no UI components
- All functionality must be testable via pytest
- Must support parallel test execution without conflicts
- Should integrate with common test frameworks (pytest, unittest, behave)

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The mock server must provide:

1. **Test Harness Control API**: A comprehensive API allowing test scripts to configure mocks, set up response sequences, and query assertion results during test execution.

2. **Sequence Management Engine**: A system for defining and executing deterministic response sequences that can simulate complex multi-step workflows with state transitions.

3. **Assertion Recorder**: A mechanism that captures all incoming requests and allows tests to verify that expected calls were made with correct parameters.

4. **Namespace Isolation Manager**: A system that provides complete isolation between different test suites running concurrently, preventing any cross-contamination of mock states.

5. **BDD Integration Layer**: Support for Cucumber/Gherkin scenario tags that automatically configure appropriate mock responses based on test scenario definitions.

## Testing Requirements

### Key Functionalities to Verify
- Runtime configuration changes take effect immediately
- Response sequences play back deterministically
- Assertion recording captures all request details accurately
- Namespace isolation prevents any cross-test interference
- BDD tag mapping correctly configures mock responses

### Critical User Scenarios
- Configuring mock responses mid-test for state transitions
- Running multiple test suites in parallel with different mock configs
- Verifying complex request sequences in multi-step workflows
- Resetting mock state between test scenarios
- Mapping Cucumber scenarios to specific mock behaviors

### Performance Benchmarks
- Configuration API response time under 50ms
- Support for 50+ concurrent test namespaces
- Assertion query performance under 10ms
- State reset completion under 100ms
- No performance degradation with 1000+ recorded requests

### Edge Cases and Error Conditions
- Handling conflicting configuration requests
- Recovery from malformed test harness commands
- Namespace creation with duplicate names
- Assertion queries for non-existent requests
- BDD tag mapping with undefined scenarios

### Required Test Coverage
- Minimum 95% code coverage for all core modules
- 100% coverage for isolation and state management
- Integration tests for all API endpoints
- Concurrency tests for namespace isolation
- End-to-end tests with actual test frameworks

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

1. Test suites can dynamically control mock behavior during execution
2. All test runs produce deterministic, repeatable results
3. Parallel test execution works without any interference
4. Integration with BDD frameworks is seamless and intuitive
5. Performance meets all specified benchmarks

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
4. Showing successful integration with test automation frameworks

**CRITICAL**: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion.