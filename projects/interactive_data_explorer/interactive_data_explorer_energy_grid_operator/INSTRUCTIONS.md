# Power Distribution Analysis Explorer

A specialized interactive data exploration framework tailored for energy grid operators to monitor, analyze, and optimize power distribution networks for reliability and efficiency.

## Overview

This project provides a comprehensive data analysis library for energy grid operators to visualize grid topology, identify anomalies, forecast load, analyze renewable integration, and simulate failure scenarios. The Power Distribution Analysis Explorer enables operators to ensure reliable service through sophisticated data analysis of consumption patterns, equipment performance, and grid stability metrics.

## Persona Description

Chen monitors power distribution networks to ensure reliable service and efficient load balancing. He needs to analyze consumption patterns, identify potential failure points, and optimize power distribution across the grid.

## Key Requirements

1. **Grid Topology Visualization**
   - Implement network analysis tools for showing load distribution across grid segments
   - Critical for understanding current power flows and identifying congestion points
   - Must handle complex network topologies with substations, transformers, and distribution lines
   - Enables operators to visualize the current state of the grid and identify stress points

2. **Anomaly Detection**
   - Create statistical algorithms for early warning of potential equipment failures
   - Essential for preventing outages through proactive maintenance
   - Must analyze time-series data from various grid sensors and equipment monitors
   - Allows operators to identify unusual patterns that may indicate impending failures or instabilities

3. **Load Forecasting Tools**
   - Develop predictive models for demand patterns based on weather and usage history
   - Vital for anticipating demand fluctuations and ensuring sufficient capacity
   - Must integrate multiple data sources including weather forecasts and historical consumption
   - Helps operators schedule generation resources efficiently to meet anticipated demand

4. **Renewable Integration Analysis**
   - Implement analysis capabilities for showing impact of variable energy sources
   - Important for managing the integration of intermittent renewable power into the grid
   - Must model the variability of solar and wind power and its effects on grid stability
   - Enables operators to maintain grid reliability while maximizing renewable energy utilization

5. **Cascading Failure Simulation**
   - Create simulation tools for identifying critical points in the distribution network
   - Critical for understanding vulnerability and resilience of the power grid
   - Must model propagation of failures across interconnected grid components
   - Allows operators to identify and reinforce vulnerable points to prevent widespread outages

## Technical Requirements

### Testability Requirements
- All grid analysis algorithms must be verifiable against known test networks
- Anomaly detection must be validated against historical equipment failure data
- Forecasting models must be testable against historical demand records
- Renewable integration analysis must be verifiable with actual production data
- Failure simulations must produce consistent results with identical inputs

### Performance Expectations
- Must efficiently handle grid networks with thousands of nodes and connections
- Time-series analysis should process historical data covering at least one year in under a minute
- Forecasting calculations should complete in under 30 seconds for week-ahead predictions
- Simulation of cascading failures should complete in under 20 seconds for typical scenarios
- Visualization generation should complete in under 5 seconds for interactive analysis

### Integration Points
- Data import capabilities for common grid management system formats
- Support for weather data services and forecasts
- Integration with SCADA and other industrial control systems
- Export interfaces for sharing findings with other operational tools
- Optional integration with GIS data for geographical context

### Key Constraints
- Must operate with Python's standard library and minimal external dependencies
- No user interface components; focus on API and programmatic interfaces
- All operations must function with sensitive grid infrastructure data
- Must handle time-series data with varying sampling rates and quality
- All analysis must be reproducible with identical inputs producing identical results

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Power Distribution Analysis Explorer should provide a cohesive set of Python modules that enable:

1. **Grid Network Analysis**
   - Loading and processing power distribution network topology
   - Calculating power flows and load distribution
   - Identifying bottlenecks and congestion points
   - Assessing network reliability and redundancy

2. **Equipment Health Monitoring**
   - Processing time-series data from grid equipment sensors
   - Detecting anomalous behavior patterns
   - Estimating remaining useful life of critical components
   - Prioritizing maintenance based on failure risk

3. **Demand Forecasting**
   - Analyzing historical consumption patterns across different time scales
   - Incorporating weather predictions into load forecasts
   - Modeling special events and anomalous demand conditions
   - Generating confidence intervals for demand predictions

4. **Renewable Energy Management**
   - Modeling production variability of renewable sources
   - Analyzing correlation between renewable production and demand
   - Optimizing storage utilization to buffer variability
   - Calculating reserve requirements based on renewable uncertainty

5. **Resilience Analysis**
   - Simulating failure scenarios with various initial conditions
   - Identifying critical nodes where failures have cascading effects
   - Evaluating contingency plans for major disruptions
   - Quantifying resilience metrics for different grid configurations

## Testing Requirements

### Key Functionalities to Verify
- Accurate modeling of power flow distribution across the grid network
- Correct identification of equipment anomalies in sensor data
- Proper forecasting of load patterns based on historical data and weather
- Effective analysis of renewable energy integration challenges
- Realistic simulation of cascading failures in the grid

### Critical User Scenarios
- Analyzing power flow during peak demand periods to identify congestion
- Detecting early warning signs of transformer failure from sensor data
- Forecasting next-day load requirements with weather event considerations
- Assessing grid stability with increasing solar generation during cloud transitions
- Simulating the impact of a substation failure on the broader network

### Performance Benchmarks
- Process grid topology data for a regional network (5,000+ nodes) in under 30 seconds
- Analyze equipment sensor data (1,000+ sensors with year-long history) in under 60 seconds
- Generate 7-day load forecasts incorporating weather predictions in under 30 seconds
- Model renewable integration scenarios in under 20 seconds
- Simulate cascading failure scenarios in under 15 seconds for standard test cases

### Edge Cases and Error Conditions
- Graceful handling of sensor data gaps and communication failures
- Appropriate management of extreme weather events in forecasting
- Correct processing of islanding events and grid segmentation
- Robust handling of rapid fluctuations in renewable generation
- Proper error messages for physically impossible or unstable grid configurations

### Required Test Coverage Metrics
- Minimum 90% line coverage for all grid analysis algorithms
- 100% coverage of all anomaly detection and forecasting functions
- Comprehensive test cases for renewable integration analysis
- Integration tests for all supported data formats and sources
- Performance tests for all computationally intensive operations

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. All key requirements are implemented and demonstrable through programmatic interfaces
2. Comprehensive tests verify the functionality against realistic power grid scenarios
3. The system can accurately visualize load distribution across grid topology
4. Anomaly detection correctly identifies potential equipment failures
5. Load forecasting tools effectively predict demand patterns
6. Renewable integration analysis accurately models variable generation impacts
7. Cascading failure simulation realistically predicts failure propagation
8. All performance benchmarks are met or exceeded
9. The implementation follows clean code principles with proper documentation
10. The API design is intuitive for Python-literate grid operators

## Development Environment Setup

To set up the development environment for this project:

1. Create a new Python library project:
   ```
   uv init --lib
   ```

2. Install development dependencies:
   ```
   uv sync
   ```

3. Run tests:
   ```
   uv run pytest
   ```

4. Run a specific test:
   ```
   uv run pytest tests/test_load_forecasting.py::test_weather_integration
   ```

5. Run the linter:
   ```
   uv run ruff check .
   ```

6. Format the code:
   ```
   uv run ruff format
   ```

7. Run the type checker:
   ```
   uv run pyright
   ```

8. Run a Python script:
   ```
   uv run python examples/analyze_grid_topology.py
   ```