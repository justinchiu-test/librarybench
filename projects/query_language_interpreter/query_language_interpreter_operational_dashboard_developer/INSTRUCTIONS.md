# Manufacturing Operations Query Interpreter

A specialized query language interpreter for real-time manufacturing monitoring with support for sliding time windows, threshold alerts, equipment hierarchy traversal, statistical process control, and production schedule integration.

## Overview

This project implements a query language interpreter designed specifically for manufacturing operations monitoring. It allows dashboard developers to query live production data, historical trends, and alert conditions without impacting operational systems. The interpreter includes sliding time window calculations, threshold monitoring, equipment hierarchy traversal, statistical process control functions, and production schedule integration—essential features for creating effective operational dashboards for manufacturing environments.

## Persona Description

Miguel creates real-time monitoring displays for manufacturing processes. He needs to query live production data, historical trends, and alert conditions without impacting operational systems.

## Key Requirements

1. **Sliding Time Window Computations**
   - Implement configurable time window operations that continuously update with new data
   - Support various window types (tumbling, sliding, session) with flexible duration
   - Enable window-based aggregations and calculations (min, max, avg, rate of change)
   - Include horizon queries that combine historical data with real-time readings
   - Critical for Miguel to show recent metrics with appropriate historical context, enabling operators to see trends, patterns, and sudden changes in manufacturing processes

2. **Threshold Monitoring Expressions**
   - Support complex condition expressions for monitoring process parameters
   - Enable multi-level thresholds with different severity levels and persistence requirements
   - Implement compound conditions with temporal aspects (e.g., exceeded for >5 minutes)
   - Include notification hooks and alert state tracking
   - Essential for automatically detecting and alerting when manufacturing processes deviate from expected parameters, allowing proactive intervention

3. **Equipment Hierarchy Traversal**
   - Implement query operations across equipment hierarchies (plant→area→line→machine→sensor)
   - Support property inheritance and aggregation up the hierarchy
   - Enable drill-down filtering based on hierarchical relationships
   - Include metadata-based filtering across hierarchy levels
   - Crucial for analyzing data at appropriate levels of detail, from individual sensors to plant-wide metrics, allowing flexible views for different operational needs

4. **Statistical Process Control Functions**
   - Implement SPC calculations (control limits, capability indices, run rules)
   - Support various control chart types (X-bar, R, individuals, etc.)
   - Enable detection of statistical process violations
   - Include capability analysis for process evaluation
   - Important for monitoring manufacturing quality using statistical methods, identifying non-random variations, and ensuring processes remain within control limits

5. **Production Schedule Integration**
   - Correlate measurement data with planned production activities and schedules
   - Enable querying by production batch, product type, or planned operation
   - Support schedule-based filtering and aggregation
   - Include variance calculations between actual and scheduled metrics
   - Critical for understanding measurement data in the context of what was being produced, allowing analysis of process performance by product type, batch, or operation

## Technical Requirements

### Testability Requirements
- Sliding window calculations must be verifiable with synthetic time-series data
- Threshold monitoring must trigger on predefined test conditions
- Hierarchy traversal must maintain proper relationships in test equipment structures
- SPC functions must produce correct statistical results for known test cases
- Schedule integration must correctly correlate test schedule data with measurements

### Performance Expectations
- Process 10,000 data points per second for real-time dashboard queries
- Support equipment hierarchies with up to 50,000 elements
- Calculate SPC metrics for 1,000 process points in under 5 seconds
- Return time window results for 24 hours of 1-second data in under 3 seconds
- Update threshold status for 500 monitored conditions in under 1 second

### Integration Points
- Connect to industrial data sources (OPC UA, MQTT, historians)
- Import production schedule data from MES systems
- Export alert information to notification systems
- Provide dashboard visualization-ready output formats
- Support integration with existing manufacturing systems

### Key Constraints
- Must not impact operational control systems or add significant network load
- Query processing should prioritize real-time data over historical for dashboard updates
- All operations must be read-only to production systems
- Memory usage must scale efficiently with number of monitored points
- Must operate reliably in industrial computing environments

## Core Functionality

The core of this Query Language Interpreter includes:

1. **Time-Series Data Processor**
   - Handle continuous streams of sensor data
   - Implement efficient sliding window calculations
   - Support high-frequency data ingestion
   - Manage data retention policies

2. **Equipment Model Manager**
   - Maintain equipment hierarchy relationships
   - Support inheritance of properties and metadata
   - Enable efficient hierarchy traversal
   - Manage equipment state information

3. **Statistical Analysis Engine**
   - Calculate standard SPC metrics
   - Identify statistical violations and patterns
   - Support process capability assessment
   - Provide statistical significance evaluation

4. **Alert Condition Evaluator**
   - Process threshold expressions efficiently
   - Track alert states and durations
   - Manage alert priorities and categories
   - Support complex compound conditions

5. **Schedule Integration System**
   - Correlate time-series data with schedule events
   - Handle schedule changes and adjustments
   - Support batch and order-based filtering
   - Enable product-specific analysis

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of sliding window calculations for various window types
- Correct triggering of threshold alerts under defined conditions
- Proper traversal of equipment hierarchies and aggregations
- Accurate calculation of SPC metrics and control limits
- Correct correlation of measurements with production schedule items

### Critical User Scenarios
- Monitoring real-time production metrics across multiple lines
- Detecting quality deviations through statistical process control
- Analyzing performance trends for specific equipment
- Comparing process parameters across different product runs
- Identifying correlation between schedule changes and process variations

### Performance Benchmarks
- Update dashboards with 100+ metrics at least once per second
- Process hierarchy aggregations for 10,000 points in under 5 seconds
- Calculate SPC metrics for 50 process variables with 1-month history in under 10 seconds
- Evaluate 200 threshold conditions in under 500ms
- Join production data with schedule information at a rate of 5,000 records per second

### Edge Cases and Error Conditions
- Handling sensor communication interruptions
- Managing clock synchronization issues across distributed systems
- Dealing with missing values in time-series data
- Processing unexpected equipment hierarchy changes
- Handling production schedule changes and adjustments

### Required Test Coverage Metrics
- 95% code coverage for window calculation functions
- 100% coverage for threshold condition evaluation
- Comprehensive tests for hierarchy traversal operations
- Validation of SPC calculations against reference implementations
- Performance testing under maximum expected data volumes

## Success Criteria

1. Sliding time windows accurately represent recent metrics with appropriate historical context
2. Threshold monitoring reliably detects and alerts on process deviations
3. Equipment hierarchy traversal enables analysis at appropriate organizational levels
4. SPC functions correctly identify statistical process variations
5. Production schedule integration successfully correlates measurements with planned activities
6. Dashboard queries consistently meet performance requirements even at peak data rates
7. System operates without negatively impacting production operations
8. Operations staff can identify issues faster than with traditional monitoring tools

## Getting Started with Development

To start developing this project:

1. Set up the development environment using `uv`:
   ```
   uv init --lib
   ```

2. Manage dependencies with `uv`:
   ```
   uv pip install numpy pandas statsmodels
   ```

3. Run your code with:
   ```
   uv run python your_script.py
   ```

4. Run tests with:
   ```
   uv run pytest
   ```