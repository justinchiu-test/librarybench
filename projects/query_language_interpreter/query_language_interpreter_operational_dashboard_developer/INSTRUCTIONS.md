# Real-Time Manufacturing Query Engine

A query language interpreter specialized for monitoring live production data with minimal impact on operational systems.

## Overview

The Real-Time Manufacturing Query Engine provides a specialized query system for monitoring manufacturing processes in real-time. This project variant focuses on enabling operational dashboard developers to query live production data, historical trends, and alert conditions without impacting operational systems, featuring sliding time windows, threshold monitoring, equipment hierarchy traversal, and statistical process control.

## Persona Description

Miguel creates real-time monitoring displays for manufacturing processes. He needs to query live production data, historical trends, and alert conditions without impacting operational systems.

## Key Requirements

1. **Sliding time window computations showing recent metrics with configurable history**
   - Implement efficient sliding window operations with tunable size and overlap
   - Support concurrent windows with different time spans (last hour, shift, day, week)
   - Enable configurable update frequencies for different time windows
   - Provide optimized memory usage for high-frequency sensor data
   - Critical for Miguel to create dashboards showing both immediate conditions and recent trends without requiring separate queries for each time frame

2. **Threshold monitoring expressions generating alerts based on query results**
   - Develop a threshold expression system with multi-condition support
   - Implement hysteresis to prevent alert flapping
   - Support relative thresholds based on historical baselines
   - Enable tiered alert levels with escalation rules
   - Essential for automatically detecting and alerting on out-of-spec conditions across hundreds of production parameters

3. **Equipment hierarchy traversal enabling drill-down from plant to specific sensors**
   - Create a flexible equipment hierarchy model supporting plant→line→cell→equipment→sensor organization
   - Support both upward and downward traversal in queries
   - Enable dynamic grouping by equipment type, location, or function
   - Provide aggregation operations at each hierarchy level
   - Vital for organizing sensor data logically and enabling drill-down analysis from high-level KPIs to root causes

4. **Statistical process control functions detecting manufacturing variations**
   - Implement core SPC algorithms (control charts, capability indices, run rules)
   - Support both standard and custom control limits
   - Enable multivariate SPC for correlated parameters
   - Provide early trend detection before limit violations
   - Important for identifying process drift, special cause variation, and quality issues before they lead to defects

5. **Production schedule integration correlating measurements with planned operations**
   - Develop methods to associate time series data with production schedule events
   - Support filtering and grouping by product, batch, order, or recipe
   - Enable automatic context switching based on current production
   - Provide schedule-aware baseline comparisons
   - Critical for understanding measurement variations in the context of production changes and properly attributing variations to specific products or processes

## Technical Requirements

### Testability Requirements
- All monitoring functions must be testable with pytest
- Test threshold expressions with comprehensive simulated data scenarios
- Verify hierarchy traversal with realistic manufacturing equipment trees
- Test SPC functions against reference implementations and standard datasets
- Validate schedule integration with realistic production plan data

### Performance Expectations
- Process high-frequency sensor data (up to 10,000 readings per second)
- Update dashboards with sub-second refresh rates for current values
- Support at least 100 concurrent dashboard sessions without performance degradation
- Maintain real-time alert detection with less than 5-second latency
- Query historical data spanning 1 year in under 10 seconds

### Integration Points
- Connect with OPC UA, MQTT, and other industrial protocols
- Interface with MES and production scheduling systems
- Support historians and time-series databases
- Integrate with alert management and notification systems
- Provide compatible outputs for visualization libraries

### Key Constraints
- Maintain minimal impact on operational technology systems
- Operate without requiring real-time database modifications
- Function with limited bandwidth between OT and IT networks
- Handle unpredictable communication interruptions
- Process diverse data types from different equipment vendors

### Implementation Notes
IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Real-Time Manufacturing Query Engine must implement the following core functionality:

1. **Time Series Data Management**
   - Efficiently process streaming sensor data
   - Manage time windows with different spans and update frequencies
   - Optimize storage and retrieval for manufacturing data patterns
   - Handle data quality issues common in industrial sensors

2. **Query Language Processor**
   - Implement specialized syntax for manufacturing analytics
   - Support equipment hierarchy traversal in queries
   - Enable schedule-aware filtering and grouping
   - Optimize query execution for minimal impact on operational systems

3. **Alert and Monitoring System**
   - Process threshold expressions in real-time
   - Implement hysteresis and debouncing for stable alerting
   - Support complex multi-condition alert logic
   - Manage alert state persistence and acknowledgment

4. **Statistical Analysis Engine**
   - Implement SPC algorithms and control charts
   - Calculate process capability and performance indices
   - Support run rules and trend detection
   - Enable correlation analysis between parameters

5. **Production Context Management**
   - Maintain current production schedule awareness
   - Associate measurements with products and batches
   - Track equipment states and operational modes
   - Support context-specific baseline calculations

## Testing Requirements

### Key Functionalities to Verify
- Accuracy of sliding window calculations at different time spans
- Reliable threshold detection and alert generation
- Correct traversal and aggregation in equipment hierarchies
- Proper implementation of SPC algorithms and run rules
- Accurate correlation of measurements with production schedule events

### Critical User Scenarios
- Monitoring real-time production parameters with configurable time horizons
- Detecting process drift and generating alerts before quality issues occur
- Drilling down from plant-level KPIs to specific equipment issues
- Comparing process behavior across different product runs
- Analyzing historical trends to optimize manufacturing parameters

### Performance Benchmarks
- Process at least 10,000 sensor readings per second
- Maintain alert detection latency under 5 seconds
- Support at least 100 concurrent dashboard sessions
- Execute equipment hierarchy traversals across 10,000 nodes in under 3 seconds
- Update sliding window calculations in less than 100ms

### Edge Cases and Error Conditions
- Handling sensor data gaps and communication interruptions
- Processing messy data with outliers and noise
- Managing rapid production schedule changes
- Dealing with equipment addition or removal during operation
- Recovering from system restarts without alert duplication

### Required Test Coverage Metrics
- Minimum 90% code coverage for all modules
- 100% coverage of alert detection and SPC functions
- Test sliding windows with at least 20 different time spans and update frequencies
- Verify hierarchy traversal with at least 5 levels of equipment nesting
- Test schedule integration with at least 10 different production scenarios

## Success Criteria

The implementation will be considered successful if it meets the following criteria:

1. **Functional Completeness**
   - All five key requirements are fully implemented
   - Sliding window calculations correctly track metrics across different time frames
   - Threshold monitoring reliably detects and alerts on abnormal conditions
   - Equipment hierarchy traversal enables effective drill-down analysis
   - SPC functions accurately identify process variations
   - Production schedule integration correctly correlates measurements with operations

2. **Performance and Scalability**
   - Meets all performance benchmarks specified
   - Operates with minimal impact on production systems
   - Scales to handle manufacturing environments with thousands of sensors
   - Supports concurrent dashboard usage by multiple users
   - Maintains responsive queries against historical data

3. **Operational Reliability**
   - Functions properly during communication interruptions
   - Handles sensor errors and data quality issues gracefully
   - Avoids false alerts and alert storms
   - Maintains data consistency during production transitions
   - Recovers automatically from system disruptions

4. **Manufacturing Intelligence**
   - Enables identification of improvement opportunities
   - Supports root cause analysis of quality issues
   - Provides actionable insights for process optimization
   - Helps prevent production problems through early detection
   - Enhances understanding of process capability and performance