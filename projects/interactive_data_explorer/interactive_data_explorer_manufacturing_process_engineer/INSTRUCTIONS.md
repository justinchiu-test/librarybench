# Manufacturing Process Analysis and Optimization Explorer

A specialized interactive data exploration framework tailored for manufacturing process engineers to identify quality issues and optimize production efficiency.

## Overview

This project provides a comprehensive data analysis library for manufacturing process engineers to explore, visualize, and identify patterns in production line data. The Manufacturing Process Analysis and Optimization Explorer enables engineers to analyze sensor data from manufacturing equipment, track state transitions, correlate defects with specific process parameters, compare shift performance, calculate equipment effectiveness, and integrate with real-time monitoring systems.

## Persona Description

Hiroshi optimizes production lines by analyzing sensor data from manufacturing equipment. He needs to identify quality issues and efficiency bottlenecks through pattern recognition in multivariate time-series data from the factory floor.

## Key Requirements

1. **Machine State Transition Visualization**
   - Implement functionality to track and visualize operational mode changes over time
   - Essential for identifying problematic state transitions that lead to quality issues or downtime
   - Must support multi-machine analysis to detect cascading failures across production lines
   - Critical for process engineers to understand equipment behavior patterns across manufacturing cycles

2. **Defect Correlation Mapping**
   - Develop statistical analysis tools to link quality issues with specific process parameters
   - Vital for root cause analysis when troubleshooting manufacturing defects
   - Must handle multivariate correlation across dozens of process parameters simultaneously
   - Enables process engineers to implement targeted process improvements rather than trial-and-error adjustments

3. **Shift Comparison Analysis**
   - Create comparative analytics to highlight performance differences between crews and schedules
   - Important for standardizing processes and identifying best practices across different shifts
   - Must account for different production runs and product variations to enable fair comparisons
   - Helps process engineers identify training needs and process standardization opportunities

4. **Production Efficiency Calculators**
   - Implement customizable OEE (Overall Equipment Effectiveness) formulas and calculations
   - Critical for quantifying production performance and tracking improvement initiatives
   - Must support both standard and customized KPI calculations relevant to specific manufacturing contexts
   - Enables process engineers to benchmark performance against industry standards and track improvement progress

5. **Real-time Monitoring Integration**
   - Develop interfaces for live data streaming from factory systems
   - Essential for catching issues as they emerge rather than through post-process analysis
   - Must handle high-frequency data streams without performance degradation
   - Allows process engineers to implement proactive process adjustments based on emerging trends

## Technical Requirements

### Testability Requirements
- All data processing and analysis functions must be independently testable without external dependencies
- Statistical algorithms must be verifiable against known test datasets with established outcomes
- Time-series analysis functions must be testable with synthetic data representing different manufacturing scenarios
- State transition tracking must demonstrate correct behavior with complex test sequences
- Performance metrics must be measurable through automated testing frameworks

### Performance Expectations
- Must efficiently handle datasets with millions of data points representing weeks of production data
- Statistical analysis operations should complete in under 5 seconds for typical dataset sizes
- Real-time monitoring must support processing at least 100 data points per second per machine
- Data loading and preprocessing should utilize efficient streaming techniques for large datasets
- Memory usage should be optimized to handle large production datasets on standard engineering workstations

### Integration Points
- Data import capabilities for common industrial control system formats (CSV, JSON, SQL databases)
- Optional API interfaces for connecting to common MES (Manufacturing Execution Systems)
- Support for reading time-series data from SCADA systems through appropriate adapters
- Export capabilities for findings in formats compatible with quality management systems
- Interfaces for accessing historical production databases

### Key Constraints
- Must operate with Python's standard library and minimal external dependencies
- No user interface components; focus on API and programmatic interfaces
- All analysis must be reproducible with identical inputs producing identical results
- Processing of sensitive production data must maintain data integrity and security
- Must account for irregular sampling rates and missing data common in manufacturing environments

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Manufacturing Process Analysis and Optimization Explorer should provide a cohesive set of Python modules that enable:

1. **Data Ingestion and Processing**
   - Loading time-series data from manufacturing equipment sensors
   - Preprocessing capabilities to handle missing values, outliers, and measurement noise
   - Time synchronization across multiple data sources with varying sampling rates
   - Data normalization and feature extraction for manufacturing contexts

2. **State Transition Analysis**
   - Detection and classification of discrete operational states from continuous sensor data
   - Statistical analysis of state duration, transition frequency, and stability
   - Correlation between state transitions and quality or performance metrics
   - Anomaly detection in state patterns compared to normal operation

3. **Quality and Defect Analysis**
   - Statistical methods to identify correlations between process parameters and quality outcomes
   - Root cause analysis tools to trace defect origins through production data
   - Pattern recognition algorithms to detect recurring quality issues
   - Predictive capabilities to identify conditions likely to lead to defects

4. **Performance Metrics and Benchmarking**
   - Calculation of OEE and component metrics (Availability, Performance, Quality)
   - Customizable KPI framework for industry and machine-specific metrics
   - Comparative analysis tools for benchmarking against historical performance
   - Shift performance analysis with normalization for product mix and other variables

5. **Real-time Data Handling**
   - Stream processing capabilities for ongoing data collection and analysis
   - Efficient data structures for updating statistics and metrics in real-time
   - Alert generation based on statistical thresholds and pattern recognition
   - Caching mechanisms for balancing real-time analysis with historical context

## Testing Requirements

### Key Functionalities to Verify
- Accurate detection of machine states from sensor data
- Correct calculation of OEE metrics under various operating conditions
- Proper identification of correlations between process parameters and defects
- Accurate comparison of performance metrics across different shifts
- Efficient processing of streaming data in real-time analysis scenarios

### Critical User Scenarios
- Analyzing a production run with multiple defect types to identify root causes
- Comparing performance across shifts with different product mixes
- Tracking machine state transitions during startup, production, and shutdown sequences
- Calculating efficiency metrics for a production line with variable product types
- Monitoring real-time data streams for emerging quality issues

### Performance Benchmarks
- Complete analysis of 1 week of production data (>1 million data points) in under 30 seconds
- Process streaming data at minimum 100 data points per second with real-time analytics
- State transition detection with accuracy >95% compared to manual classification
- Statistical correlation calculations with performance scaling linearly with data size
- Memory usage remaining below 1GB for datasets containing up to 10 million data points

### Edge Cases and Error Conditions
- Graceful handling of missing sensor data and communication interruptions
- Correct processing of data during unexpected machine shutdowns and restarts
- Appropriate error handling for invalid configuration parameters
- Robustness against corrupted or inconsistent data files
- Proper handling of machines with non-standard states or operating modes

### Required Test Coverage Metrics
- Minimum 90% line coverage for all core functionality
- 100% coverage of all statistical algorithms and data processing functions
- Comprehensive test cases for all public APIs and interfaces
- Integration tests for data loading from all supported formats
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
2. Comprehensive tests verify the functionality against real-world manufacturing scenarios
3. The system can accurately detect and visualize machine state transitions with >95% accuracy
4. Defect correlation analysis correctly identifies actual process parameter relationships
5. Shift comparison analytics provide actionable insights about performance differences
6. OEE calculations match manual calculations for test datasets within 0.1% tolerance
7. Real-time monitoring capabilities handle the required data throughput without degradation
8. All performance benchmarks are met or exceeded
9. The implementation follows clean code principles with proper documentation
10. The API design is intuitive for Python-literate manufacturing engineers

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
   uv run pytest tests/test_state_transitions.py::test_state_detection
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
   uv run python examples/analyze_production_run.py
   ```