# PyMockAPI - Performance Testing Mock Server

## Overview
A specialized HTTP API mock server designed for performance test engineers to simulate various backend performance characteristics with precision. This implementation focuses on creating controlled performance testing environments that help identify frontend bottlenecks by accurately simulating backend behavior under different load conditions.

## Persona Description
A performance engineer stress-testing frontend applications who needs to simulate various backend performance characteristics. She wants to identify frontend bottlenecks by controlling backend response times precisely.

## Key Requirements

1. **Response time distribution curves with statistical modeling**
   - Critical for simulating realistic performance patterns beyond simple delays
   - Enables testing against various latency profiles (normal, exponential, bimodal distributions)

2. **Concurrent request handling limits with queueing simulation**
   - Essential for testing frontend behavior when backends are overwhelmed
   - Allows validation of retry logic and user experience under congestion

3. **Resource exhaustion scenarios with memory/CPU constraints**
   - Vital for testing application resilience when backends approach limits
   - Enables identification of cascading failures and timeout handling

4. **Performance metric collection with export to monitoring tools**
   - Required for correlating frontend and backend performance data
   - Enables comprehensive performance analysis and bottleneck identification

5. **Load pattern scripting for realistic traffic simulation**
   - Critical for recreating production-like load scenarios
   - Allows testing of frontend behavior under various traffic patterns

## Technical Requirements

### Testability Requirements
- All performance characteristics must be precisely controllable
- Statistical distributions must be verifiable through testing
- Metric collection must be accurate and queryable
- Load patterns must be reproducible

### Performance Expectations
- Support for 1000+ requests per second
- Response time control precision within 1ms
- Statistical distribution accuracy within 2% margin
- Metric collection with minimal overhead (<5%)

### Integration Points
- API for configuring performance characteristics
- Metrics export in Prometheus/StatsD formats
- Load script definition and execution API
- Real-time performance monitoring endpoints

### Key Constraints
- Implementation must be pure Python with no UI components
- All functionality must be testable via pytest
- Must not require external load testing tools
- Should work with standard monitoring systems

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The mock server must provide:

1. **Statistical Response Timer**: A sophisticated timing system that can generate response delays following various statistical distributions (normal, exponential, Poisson, custom) with configurable parameters.

2. **Concurrency Limiter**: Request handling system with configurable connection pools, queue depths, and rejection policies to simulate backend capacity constraints.

3. **Resource Simulator**: Mechanisms to simulate CPU and memory pressure through controlled resource consumption, enabling realistic degradation scenarios.

4. **Metrics Collector**: Comprehensive performance metric collection including request rates, response times, queue depths, and resource utilization with export capabilities.

5. **Load Pattern Engine**: Scriptable system for defining and executing complex load patterns including ramp-ups, spikes, and cyclical patterns.

## Testing Requirements

### Key Functionalities to Verify
- Response time distributions match configured parameters
- Concurrency limits are enforced accurately
- Resource constraints create expected degradation
- Metrics collection is accurate and complete
- Load patterns execute as defined

### Critical User Scenarios
- Testing frontend behavior with varying backend latencies
- Validating application response to backend overload
- Identifying frontend performance cliffs
- Correlating frontend/backend performance metrics
- Simulating production load patterns

### Performance Benchmarks
- Handle 1000+ requests per second
- Response time precision within 1ms
- Distribution accuracy within 2% margin
- Metric overhead under 5%
- Support 100+ concurrent connections

### Edge Cases and Error Conditions
- Handling extreme latency values (0ms, 60s+)
- Recovery from resource exhaustion
- Queue overflow behavior
- Metric storage limitations
- Invalid distribution parameters

### Required Test Coverage
- Minimum 90% code coverage for all core modules
- 100% coverage for statistical algorithms
- Performance tests for high load scenarios
- Integration tests for metric exporters
- Statistical validation of distributions

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

1. Response time distributions accurately follow configured patterns
2. Concurrency and resource limits realistically simulate constraints
3. Performance metrics provide actionable insights
4. Load patterns can recreate production scenarios
5. Frontend bottlenecks can be reliably identified

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
4. Showing accurate performance simulation capabilities

**CRITICAL**: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion.