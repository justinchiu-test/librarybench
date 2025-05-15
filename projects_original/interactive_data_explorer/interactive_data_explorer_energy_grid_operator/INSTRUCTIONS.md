# Power Grid Data Explorer

## Overview
A terminal-based power distribution network analysis framework designed specifically for energy grid operators who need to monitor complex grid topologies, analyze consumption patterns, identify potential failure points, and optimize power distribution. This specialized tool enables real-time data exploration in control room environments without requiring graphical interfaces.

## Persona Description
Chen monitors power distribution networks to ensure reliable service and efficient load balancing. He needs to analyze consumption patterns, identify potential failure points, and optimize power distribution across the grid.

## Key Requirements
1. **Grid topology visualization** - Show load distribution across network segments to identify bottlenecks and imbalances. This functionality is critical as grid operators need to understand the real-time flow of electricity through complex interconnected networks to identify potential issues before they cause outages.

2. **Anomaly detection for equipment failures** - Implement early warning system for potential equipment failures using statistical pattern detection. Grid operators must be able to proactively identify unusual behavior patterns in transformers, substations, and transmission equipment before catastrophic failures occur.

3. **Load forecasting tools** - Predict demand patterns based on weather and usage history, essential for planning generation capacity and maintenance windows. Accurate forecasting allows operators to ensure adequate power is available while avoiding costly over-generation.

4. **Renewable integration analysis** - Show impact of variable energy sources like solar and wind on grid stability, critical for modern grid operations with increasing renewable penetration. Operators need to understand how fluctuating renewable inputs affect overall grid performance.

5. **Cascading failure simulation** - Identify critical points in the distribution network where failures could propagate, vital for understanding systemic risks and prioritizing maintenance. This feature helps prevent widespread outages by highlighting vulnerable network segments.

## Technical Requirements
- **Testability Requirements**:
  - All grid topology algorithms must be testable with standard IEEE power system test cases
  - Statistical anomaly detection must be verifiable against known failure patterns
  - Forecasting accuracy must be measurable against historical data
  - Simulation results must be reproducible and match industry-standard models
  - All transformations of grid data must maintain referential integrity

- **Performance Expectations**:
  - Must handle networks with up to 10,000 nodes and 15,000 connections
  - Real-time analysis must complete within 2 seconds for critical operations
  - Forecasting calculations should complete within 30 seconds for 7-day forecasts
  - Cascading failure simulations must run in under 60 seconds for complex scenarios
  - Memory usage must not exceed 4GB during normal operation

- **Integration Points**:
  - Support for standard power industry data formats (CIM XML, PSS/E, MATPOWER)
  - Compatible with weather data APIs for forecasting integration
  - Support for time-series database outputs from SCADA systems
  - Integration with historical operational data archives

- **Key Constraints**:
  - Must function in air-gapped control room environments without internet access
  - No dependencies on external visualization libraries or frameworks
  - All operations must be usable via keyboard-only interfaces for control room use
  - Security constraints prohibit any transmission of grid data to external systems

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The Power Grid Data Explorer must provide a comprehensive analytical framework focused on electric grid operations:

1. **Grid Topology Analysis**:
   - Load and parse grid network structures from standard industry formats
   - Calculate power flow and load distribution across network segments
   - Identify bottlenecks, congestion points, and overloaded components
   - Analyze network connectivity and resilience against component failures
   - Visualize load distribution using text-based heatmaps and network diagrams

2. **Equipment Health Monitoring**:
   - Process time-series telemetry from grid components (transformers, breakers, etc.)
   - Apply statistical models to detect abnormal operating conditions
   - Calculate equipment health indices based on operating parameters
   - Generate early warnings for potential equipment failures
   - Track maintenance history and correlate with performance indicators

3. **Load Forecasting and Planning**:
   - Integrate historical load data with weather information
   - Apply time-series forecasting algorithms (ARIMA, Prophet, etc.) to predict demand
   - Account for seasonal patterns, holidays, and special events
   - Generate confidence intervals for predicted load levels
   - Compare forecasts with available generation capacity

4. **Renewable Energy Integration**:
   - Model impact of intermittent renewable sources on grid stability
   - Calculate reserve requirements based on renewable generation forecasts
   - Analyze correlation between weather patterns and renewable output
   - Optimize conventional generation scheduling around renewable availability
   - Identify grid areas most impacted by renewable variability

5. **Failure Analysis and Simulation**:
   - Model cascading failure scenarios using power flow simulations
   - Identify critical components whose failure would cause widespread outages
   - Calculate system resilience metrics and vulnerability indices
   - Simulate protection system responses to contingency events
   - Generate prioritized maintenance recommendations based on risk analysis

## Testing Requirements
- **Key Functionalities to Verify**:
  - Grid topology representation correctly models actual power networks
  - Anomaly detection algorithms successfully identify known fault patterns
  - Load forecasting accuracy meets industry standards (MAPE < 5%)
  - Cascading failure simulations match reference implementation results
  - Renewable integration analysis correctly assesses impact on grid stability

- **Critical User Scenarios**:
  - Importing grid topology and analyzing current load distribution
  - Detecting anomalous behavior in grid equipment before failure
  - Generating accurate load forecasts for operational planning
  - Assessing impact of additional renewable capacity on grid stability
  - Identifying critical vulnerabilities in network topology

- **Performance Benchmarks**:
  - Load and analyze full grid topology (10,000 nodes) within 10 seconds
  - Process 1 week of telemetry data (5-minute intervals) within 15 seconds
  - Generate 7-day hourly load forecast within 30 seconds
  - Complete cascading failure simulation for 3 contingency events within 60 seconds
  - Memory usage below 4GB during all operations

- **Edge Cases and Error Conditions**:
  - Handling incomplete or corrupted grid topology data
  - Managing telemetry data gaps and sensor failures
  - Graceful degradation with extremely large networks
  - Adapting to unexpected renewable generation patterns
  - Detecting and reporting physically impossible grid states

- **Required Test Coverage Metrics**:
  - 90% code coverage for all core functionality
  - 100% coverage for critical safety-related functions
  - All public APIs must have integration tests
  - All numerical algorithms must have validation tests against known results

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
A successful implementation of the Power Grid Data Explorer will demonstrate:

1. Complete functionality for all 5 key requirements with comprehensive test coverage
2. Ability to handle realistic power grid datasets of appropriate scale
3. Accurate anomaly detection capabilities verified against known equipment failure patterns
4. Load forecasting accuracy meeting industry standards
5. Realistic cascading failure simulation results consistent with power flow physics

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

To set up the development environment, use:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```