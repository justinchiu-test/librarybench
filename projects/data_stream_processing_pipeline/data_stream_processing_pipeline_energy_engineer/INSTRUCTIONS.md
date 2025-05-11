# Smart Grid Data Stream Processing System

## Overview
A specialized data stream processing framework designed to monitor, analyze, and optimize power distribution networks using real-time sensor data from smart grid infrastructure. The system integrates weather data, forecasts energy demand and supply patterns, and enables intelligent grid operations to balance load and integrate renewable energy sources effectively.

## Persona Description
Marcus monitors power distribution networks using sensor data from smart grid infrastructure to balance load and integrate renewable sources. His primary goal is to forecast energy demand and supply patterns while optimizing grid operations in response to changing conditions.

## Key Requirements
1. **Predictive analytics for demand forecasting with weather integration**: Implement a forecast engine that combines historical energy usage patterns with real-time weather data and predictions to generate accurate short-term (hours) and medium-term (days) demand forecasts. This predictive capability is critical for proactively balancing grid resources and planning generation capacity to meet anticipated loads while minimizing costs.

2. **Grid topology modeling with flow analysis**: Create a dynamic model of the power distribution network that represents its physical topology and continuously updates with real-time flow data, enabling simulation of load changes and contingency scenarios. This topology awareness is essential for identifying potential constraints, planning maintenance activities, and ensuring stable operations during system reconfigurations.

3. **Renewable source intermittency handling with battery storage optimization**: Develop algorithms that predict renewable energy generation variability (solar, wind) and optimize battery storage charging/discharging cycles to compensate for intermittency. This capability enables maximum utilization of renewable resources while maintaining grid stability by using energy storage as a buffer during generation fluctuations.

4. **Load shedding prioritization during constraint periods**: Implement a framework for intelligently prioritizing and sequencing load reduction during periods of supply constraints, based on configurable policies that consider customer type, critical infrastructure, economic impact, and contractual arrangements. This prioritization ensures that when demand must be reduced, it occurs in the least disruptive and most equitable manner possible.

5. **Supply/demand balancing with price signal optimization**: Design mechanisms that use dynamic pricing signals to influence consumer behavior and adjust demand in near-real-time, helping balance supply constraints through economic incentives rather than forced curtailment. This market-based approach enables more efficient resource allocation and empowers consumers to participate actively in grid stabilization.

## Technical Requirements
- **Testability Requirements**:
  - Must support simulation with synthetic grid data
  - Needs validation against historical grid events
  - Requires reproducible testing of optimization algorithms
  - Must support verification of forecasting accuracy
  - Needs comprehensive testing of failure scenarios

- **Performance Expectations**:
  - Processing of data from at least 100,000 grid sensors
  - Forecast updates at minimum 15-minute intervals
  - Optimization algorithms execution within 30 seconds
  - Grid state estimation updates every 5 seconds
  - Support for topology models with at least 10,000 nodes and edges

- **Integration Points**:
  - SCADA and grid management systems
  - Weather data and forecast services
  - Energy market and pricing platforms
  - Battery and energy storage management systems
  - Smart meter data collection infrastructure
  - Renewable generation monitoring systems

- **Key Constraints**:
  - System must operate continuously without planned downtime
  - Optimization must respect physical grid constraints
  - Implementation must handle delayed or missing sensor data
  - Processing must prioritize grid stability over optimization
  - Solution must comply with energy regulatory requirements

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must provide a framework for smart grid data processing that:

1. Ingests data from diverse sources including:
   - Grid sensors and smart meters
   - Weather observation and forecast systems
   - Renewable generation facilities
   - Energy storage systems
   - Electricity market platforms
2. Maintains a real-time model of grid topology and state
3. Generates demand and supply forecasts at multiple time horizons
4. Implements optimization algorithms for:
   - Renewable integration and intermittency management
   - Energy storage charging/discharging cycles
   - Load balancing across grid segments
   - Demand response through price signals
   - Prioritized load shedding when required
5. Provides simulation capabilities for what-if scenario analysis
6. Detects anomalies and potential failure conditions
7. Generates operational recommendations for grid operators
8. Tracks key performance indicators and optimization metrics

The implementation should emphasize forecasting accuracy, optimization efficiency, and maintaining grid stability while maximizing renewable energy utilization and minimizing costs.

## Testing Requirements
- **Key Functionalities to Verify**:
  - Accuracy of demand forecasting with weather integration
  - Correctness of grid topology modeling and flow analysis
  - Effectiveness of renewable intermittency handling
  - Appropriate load shedding prioritization logic
  - Proper implementation of supply/demand balancing through price signals

- **Critical User Scenarios**:
  - Grid operations during peak demand periods
  - Integration of variable renewable generation during adverse weather
  - Response to sudden generation or transmission capacity loss
  - Management of demand during supply constraints
  - Optimization of economic dispatch with price-responsive load

- **Performance Benchmarks**:
  - Demand forecast accuracy within 5% mean absolute percentage error
  - Optimization algorithm execution within 30 seconds
  - Grid state estimation within 99% accuracy compared to measured values
  - Renewable integration enabling at least 90% utilization of available generation
  - System capable of processing 100,000+ sensor updates per minute

- **Edge Cases and Error Conditions**:
  - Handling of communication failures with grid sensors
  - Operation during weather forecast inaccuracies
  - Response to unexpected renewable generation fluctuations
  - Behavior during grid reconfiguration or maintenance
  - Management of cascading constraint violations

- **Required Test Coverage Metrics**:
  - 100% coverage of optimization and forecasting algorithms
  - >90% line coverage for all production code
  - 100% validation against historical grid scenarios
  - Comprehensive tests for all operational states
  - Performance verification at scale with full sensor complement

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
A successful implementation will demonstrate:

1. Accurate demand forecasting that incorporates weather data
2. Effective modeling of grid topology with real-time flow analysis
3. Intelligent handling of renewable generation intermittency
4. Appropriate prioritization during load shedding events
5. Efficient balancing of supply and demand through price signals
6. Optimized operation of the grid under various conditions
7. Comprehensive test coverage with all tests passing

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions

To setup the development environment:

1. Use `uv venv` to create a virtual environment
2. From within the project directory, activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```