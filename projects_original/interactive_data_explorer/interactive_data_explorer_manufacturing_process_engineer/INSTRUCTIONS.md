# Manufacturing Process Data Explorer

## Overview
A specialized terminal-based data analysis framework designed for manufacturing process engineers who need to analyze sensor data from production equipment, identify quality issues, and detect efficiency bottlenecks. This tool enables comprehensive analysis of multivariate time-series data from factory environments to optimize production processes.

## Persona Description
Hiroshi optimizes production lines by analyzing sensor data from manufacturing equipment. He needs to identify quality issues and efficiency bottlenecks through pattern recognition in multivariate time-series data from the factory floor.

## Key Requirements
1. **Machine state transition visualization** - Create clear representations showing operational mode changes over time, essential for understanding when and how frequently equipment transitions between different states (startup, production, idle, maintenance, error). This visualization helps identify inefficient state cycling and unexpected operational patterns.

2. **Defect correlation mapping** - Implement analysis techniques to link quality issues with specific process parameters, allowing engineers to identify which machine settings or environmental conditions most strongly correlate with product defects. This capability is critical for root cause analysis of quality problems.

3. **Shift comparison views** - Generate visualizations highlighting performance differences between crews, schedules, and time periods to identify variability in production efficiency related to human factors. Understanding these differences helps standardize best practices and target training opportunities.

4. **Production efficiency calculators** - Provide customizable OEE (Overall Equipment Effectiveness) formulas and related metrics to quantify production line performance across availability, performance, and quality dimensions. These standardized metrics are crucial for benchmarking and tracking improvement initiatives.

5. **Real-time monitoring integration** - Enable connection to live data streams from factory systems to support continuous monitoring and rapid response to developing issues. This capability allows engineers to detect and address problems before they result in significant quality or efficiency losses.

## Technical Requirements
- **Testability Requirements**:
  - State transition logic must be verifiable with known production sequence data
  - Correlation algorithms must reliably identify known relationships in test datasets
  - Efficiency calculations must match manual calculations for reference datasets
  - Time series analysis functions must be validated against established statistical methods
  - All data transformations must preserve measurement precision and units

- **Performance Expectations**:
  - Must handle datasets with up to 100 sensor streams at 1-second resolution for 30 days
  - Analysis operations should complete within 5 seconds for most functions
  - State transition analysis should process 1 million state changes within 10 seconds
  - Memory usage must remain below 4GB even with large datasets
  - Real-time integration must support up to 1000 data points per second

- **Integration Points**:
  - Support for common industrial data formats (CSV, JSON, OPC UA exports, MQTT messages)
  - Import capability for machine specifications and operational parameters
  - Export functionality for report generation in standard formats
  - APIs for connecting to factory data systems (historians, MES, SCADA)
  - Integration with maintenance scheduling and quality tracking systems

- **Key Constraints**:
  - Must function in restricted factory environments with limited connectivity
  - All visualizations must be terminal-compatible without external dependencies
  - Analysis must be reproducible with consistent results for audit purposes
  - Data processing must preserve appropriate precision for manufacturing tolerances
  - System must handle interrupted or missing data common in factory environments

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The Manufacturing Process Data Explorer must provide a comprehensive framework for industrial process analysis:

1. **Machine State Analysis**:
   - Parse and interpret machine state logs from various equipment types
   - Calculate state duration statistics and transition frequencies
   - Identify abnormal state sequences and unexpected transitions
   - Generate state transition diagrams and timeline visualizations
   - Apply pattern recognition to detect recurring operational sequences

2. **Quality Control Analysis**:
   - Correlate process parameters with quality measurements
   - Implement statistical process control (SPC) calculations
   - Identify critical parameters affecting product quality
   - Apply multivariate analysis to detect complex quality relationships
   - Generate visualizations highlighting quality-parameter relationships

3. **Performance Analysis**:
   - Calculate OEE and component metrics (availability, performance, quality)
   - Implement customizable efficiency formulas for different production contexts
   - Compare performance across different time periods, crews, and products
   - Identify production bottlenecks and cycle time variations
   - Generate performance trend visualizations and benchmark comparisons

4. **Time Series Analysis**:
   - Process and clean sensor data from multiple sources
   - Apply filtering and smoothing techniques appropriate for industrial signals
   - Detect anomalies and outliers in sensor readings
   - Identify cyclic patterns and trends in process variables
   - Implement forecasting for predictive maintenance applications

5. **Real-time Data Integration**:
   - Establish connections to industrial data sources (OPC UA, MQTT, databases)
   - Implement efficient data buffering and processing streams
   - Provide real-time statistical calculations and alerting
   - Support configurable sampling and aggregation strategies
   - Ensure robust handling of connection interruptions and data gaps

## Testing Requirements
- **Key Functionalities to Verify**:
  - Machine state transition analysis correctly identifies operational patterns
  - Defect correlation correctly links quality issues with causal process parameters
  - Shift comparison accurately identifies significant performance differences
  - OEE calculations match industry standard definitions and manual calculations
  - Real-time integration correctly processes streaming data without loss

- **Critical User Scenarios**:
  - Analyzing machine state logs to identify inefficient operational patterns
  - Correlating process parameters with product quality measurements
  - Comparing efficiency metrics between different production shifts
  - Calculating OEE and related metrics from production data
  - Processing real-time streams to detect developing issues

- **Performance Benchmarks**:
  - Process 30 days of 1-second resolution data (100 sensors) within 20 seconds
  - Complete correlation analysis between 50 parameters and quality measures within 10 seconds
  - Generate state transition visualization for 1 week of operations within 5 seconds
  - Calculate performance metrics across 10 different shifts within 3 seconds
  - Handle 1000 sensor readings per second in real-time mode

- **Edge Cases and Error Conditions**:
  - Managing inconsistent timestamps or clock drift in sensor data
  - Handling missing data points or sensor failures
  - Processing data during equipment configuration changes
  - Dealing with outliers and measurement errors
  - Managing schema changes in equipment data formats

- **Required Test Coverage Metrics**:
  - 90% code coverage for all core functionality
  - 100% coverage for critical calculation functions
  - All data parsers tested with valid and malformed input
  - Complete integration tests for all public APIs
  - Stress tests for real-time processing capabilities

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
A successful implementation of the Manufacturing Process Data Explorer will demonstrate:

1. Clear visualization of machine state transitions and operational patterns
2. Accurate correlation of process parameters with quality measurements
3. Insightful comparison of performance metrics across different shifts
4. Correct calculation of OEE and related efficiency metrics
5. Robust handling of real-time data streams from factory systems

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