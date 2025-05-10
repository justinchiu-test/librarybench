# IoT Time-Series Query Interpreter

A specialized query language interpreter for IoT data analysis with support for time window operations, downsampling, anomaly detection, device hierarchy traversal, and intermittent connectivity handling.

## Overview

This project implements a query language interpreter designed specifically for Internet of Things (IoT) applications. It allows developers to query time-series measurements and device status information from distributed sensors without centralizing all data. The interpreter includes time window operations, downsampling capabilities, anomaly detection, device hierarchy traversal, and mechanisms for handling intermittent connectivity—critical features for processing and analyzing IoT sensor data effectively.

## Persona Description

Jamal builds IoT applications that process sensor data from thousands of distributed devices. He needs to query time-series measurements and device status information at the edge and in central systems.

## Key Requirements

1. **Time Window Operations**
   - Implement specialized operators for continuous sensor data streams (sliding windows, tumbling windows, session windows)
   - Support configurable window sizes based on time duration or event counts
   - Enable window-based aggregations (min, max, avg, percentiles) optimized for time-series data
   - Include window join operations across different sensor streams
   - Critical for Jamal to analyze sensor readings over specific time periods, detect patterns in continuous data streams, and perform time-based calculations across many devices

2. **Downsampling Functions**
   - Provide methods to reduce data resolution while preserving important patterns
   - Support various downsampling strategies (average, min/max preserve, priority points, etc.)
   - Enable dynamic resolution adjustment based on query needs
   - Include error estimation for downsampled results
   - Essential for balancing query performance against result precision, particularly when analyzing long time periods or when network bandwidth is constrained

3. **Anomaly Filters**
   - Implement statistical and pattern-based anomaly detection for sensor readings
   - Support device-specific normal behavior profiles
   - Enable distinction between data outliers and genuine device anomalies
   - Include confidence scoring for anomaly detection
   - Crucial for separating unusual device readings from normal variations, helping Jamal identify potential device malfunctions or important environmental changes

4. **Device Hierarchy Traversal**
   - Enable navigation and querying across hierarchical device organizations (buildings→floors→rooms→devices)
   - Support inheritance of properties and aggregation up the hierarchy
   - Provide methods to query groups of related sensors through their relationships
   - Include dynamic restructuring of hierarchies based on operational needs
   - Important for organizing and analyzing data from networks of interconnected sensors and enabling queries across logical groups of devices

5. **Intermittent Connectivity Handling**
   - Implement query mechanisms that work with partial or delayed data
   - Support progressive query results that improve as more data arrives
   - Enable store-and-forward query execution at the edge
   - Include completion tracking and notification for long-running distributed queries
   - Critical for environments where sensors may have unreliable network connections, allowing meaningful analysis despite connectivity challenges

## Technical Requirements

### Testability Requirements
- Time window operations must be verifiable with predictable test data streams
- Downsampling must maintain key statistical properties in test datasets
- Anomaly detection must identify known anomalies in synthetic data
- Hierarchy traversal must respect device relationships in test configurations
- Intermittent connectivity handling must be testable with simulated network conditions

### Performance Expectations
- Process 10,000 data points per second for basic time-series queries
- Support hierarchies with up to 100,000 devices
- Complete downsampling operations at a rate of 1 million points per minute
- Anomaly detection overhead should not exceed 20% of query time
- Respond to simple edge-device queries in under 100ms

### Integration Points
- Import data from standard IoT protocols (MQTT, CoAP, etc.)
- Support for various time-series data formats
- Export capabilities to IoT visualization platforms
- Edge computing compatibility for local query processing
- Integration with IoT device management platforms

### Key Constraints
- Must operate within memory constraints of edge devices (as low as 512MB RAM)
- Query language should be lightweight enough for embedded systems
- Operations must degrade gracefully with missing data
- Need to support both real-time and historical queries
- Must support secure data access controls

## Core Functionality

The core of this Query Language Interpreter includes:

1. **Time-Series Data Processor**
   - Handle continuous streaming data sources
   - Implement efficient time-based indexing
   - Support various time formats and timezones
   - Process irregular time intervals

2. **Window Operation Engine**
   - Calculate window boundaries efficiently
   - Apply aggregation functions over windows
   - Support sliding window advancement
   - Handle late-arriving data points

3. **Device Relationship Manager**
   - Maintain device hierarchy information
   - Support queries across related devices
   - Implement efficient hierarchy traversal
   - Handle dynamic hierarchy changes

4. **Distributed Query Coordinator**
   - Dispatch queries to appropriate devices
   - Manage result aggregation from multiple sources
   - Handle interrupted connections gracefully
   - Support progressive result delivery

5. **Data Quality System**
   - Implement anomaly detection algorithms
   - Track data completeness and reliability
   - Support confidence intervals for results
   - Provide data quality metrics

## Testing Requirements

### Key Functionalities to Verify
- Correct calculation of time window boundaries and contents
- Preservation of critical patterns during downsampling
- Accurate identification of anomalies in sensor data
- Proper traversal of device hierarchies
- Correct handling of intermittent connectivity scenarios

### Critical User Scenarios
- Monitoring environmental conditions across multiple facilities
- Detecting equipment failures through sensor pattern analysis
- Analyzing energy consumption patterns across device groups
- Correlating events across physically distributed sensors
- Performing edge analytics with limited connectivity

### Performance Benchmarks
- Process 1 million sensor readings in under 60 seconds
- Complete hierarchical aggregation queries across 10,000 devices in under 30 seconds
- Downsample 1 year of hourly data to daily summaries in under 10 seconds
- Return anomaly detection results for 100,000 data points in under 60 seconds
- Execute distributed queries with 50% of devices offline in under 2 minutes

### Edge Cases and Error Conditions
- Handling sensor data with irregular time intervals
- Managing clock drift across distributed devices
- Dealing with conflicting data from redundant sensors
- Processing partially corrupted sensor readings
- Recovering from interruptions in long-running queries

### Required Test Coverage Metrics
- 95% code coverage for time window operations
- 100% coverage for hierarchy traversal functions
- Comprehensive tests for all downsampling methods
- Validation of anomaly detection with known patterns
- Simulation testing for intermittent connectivity scenarios

## Success Criteria

1. Time window queries produce correct results across various window configurations
2. Downsampled data preserves key patterns while reducing data volume
3. Anomaly detection successfully identifies unusual device behavior
4. Device hierarchy queries properly navigate and aggregate across different levels
5. Queries complete successfully despite intermittent device connectivity
6. System functions within the resource constraints of edge computing environments
7. Query response times meet or exceed performance benchmarks
8. IoT developers can integrate the query system with minimal adaptation

## Getting Started with Development

To start developing this project:

1. Set up the development environment using `uv`:
   ```
   uv init --lib
   ```

2. Manage dependencies with `uv`:
   ```
   uv pip install numpy pandas
   ```

3. Run your code with:
   ```
   uv run python your_script.py
   ```

4. Run tests with:
   ```
   uv run pytest
   ```