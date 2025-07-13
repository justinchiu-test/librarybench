# IoT Data Archive System

## Overview
A specialized archive management system designed for IoT data engineers to efficiently compress time-series sensor data while enabling quick queries and analysis on archived metrics without full extraction.

## Persona Description
A systems engineer collecting sensor data from thousands of IoT devices. They need to compress time-series data efficiently while enabling quick queries on archived metrics.

## Key Requirements

1. **Time-Series Optimized Compression Algorithms for Sensor Data**
   - Critical for achieving high compression ratios on repetitive sensor readings
   - Implement delta encoding for sequential timestamp compression
   - Use variable-length encoding for sensor value differences
   - Support different algorithms for different data types (temperature, pressure, etc.)
   - Provide adaptive compression based on data characteristics

2. **Archive Partitioning by Device ID and Time Windows**
   - Essential for parallel processing and efficient data retrieval
   - Partition data by device ID for device-specific queries
   - Create time-based partitions (hourly, daily, monthly)
   - Support multi-dimensional partitioning strategies
   - Enable partition pruning for query optimization

3. **In-Archive Data Aggregation for Computing Statistics Without Extraction**
   - Necessary for analytics without decompressing entire datasets
   - Calculate min/max/avg/sum directly on compressed data
   - Support percentile calculations and standard deviations
   - Enable time-window aggregations (5-min, hourly averages)
   - Provide approximate query results for faster responses

4. **Streaming Compression for Continuous Data Archiving from Live Sources**
   - Required for real-time data ingestion from IoT devices
   - Implement streaming compression with minimal latency
   - Support out-of-order data arrival and late data handling
   - Maintain compression efficiency with small batch sizes
   - Enable concurrent streams from multiple devices

5. **Archive Schema Evolution Support for Changing Sensor Configurations**
   - Critical for handling IoT deployments where sensors change over time
   - Support adding/removing sensor channels without rewriting archives
   - Handle data type changes and unit conversions
   - Maintain backward compatibility with older data formats
   - Track schema versions and migration paths

## Technical Requirements

### Testability Requirements
- All functions must be thoroughly testable via pytest
- Mock IoT data streams for consistent testing
- Simulate various sensor data patterns
- Test with realistic time-series datasets

### Performance Expectations
- Compress 1 million data points per second
- Achieve 20:1 or better compression ratio for typical sensor data
- Query aggregate statistics in under 100ms
- Support 10,000+ concurrent device streams
- Handle archives with billions of data points

### Integration Points
- MQTT/AMQP for real-time data ingestion
- Time-series databases (InfluxDB, TimescaleDB)
- Stream processing frameworks (Kafka, Pulsar)
- Analytics platforms (Spark, Flink)
- IoT platforms (AWS IoT, Azure IoT Hub)

### Key Constraints
- Maintain microsecond timestamp precision
- Preserve data accuracy for scientific applications
- Support various sensor data types and formats
- Handle unreliable network connections

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The IoT data archive tool must provide:

1. **Time-Series Compression**
   - Delta encoding implementation
   - Variable-length encoding
   - Data type specific algorithms
   - Compression ratio optimization
   - Adaptive algorithm selection

2. **Partitioning System**
   - Device-based partitioning
   - Time window management
   - Partition metadata indexing
   - Query routing logic
   - Partition maintenance

3. **In-Archive Analytics**
   - Statistical computations
   - Aggregation functions
   - Approximate queries
   - Time-based rollups
   - Parallel processing

4. **Streaming Pipeline**
   - Real-time compression
   - Buffer management
   - Late data handling
   - Stream multiplexing
   - Backpressure control

5. **Schema Management**
   - Version tracking
   - Migration support
   - Compatibility checking
   - Metadata evolution
   - Type conversion

## Testing Requirements

### Key Functionalities to Verify
- Compression algorithms achieve expected ratios for different data types
- Partitioning correctly isolates data by device and time
- Aggregations produce accurate results without extraction
- Streaming compression maintains data integrity under load
- Schema evolution preserves data accessibility across versions

### Critical User Scenarios
- Archive 1 million temperature readings from 1000 devices
- Query average temperature for specific device over past month
- Compute hourly aggregates for all devices in parallel
- Ingest real-time data from newly deployed sensors
- Migrate archive when sensors add new measurement channels

### Performance Benchmarks
- Compress 1GB of sensor data in under 10 seconds
- Execute aggregate query across 1 year of data in under 1 second
- Ingest 100,000 messages per second with streaming compression
- Partition 1TB dataset across 1000 devices in under 1 hour
- Apply schema migration to 100GB archive in under 30 minutes

### Edge Cases and Error Conditions
- Handle devices with intermittent connectivity
- Process data with missing or corrupt timestamps
- Manage schema conflicts between device versions
- Deal with extreme sensor value outliers
- Recover from partial write failures

### Required Test Coverage
- Minimum 90% code coverage
- All compression algorithms thoroughly tested
- Partitioning logic must have 100% coverage
- Streaming edge cases fully validated
- Schema evolution paths tested

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

1. **Compression Efficiency**: Achieves 20:1 or better ratio for typical IoT data
2. **Query Performance**: Aggregate queries complete in sub-second time
3. **Streaming Capability**: Handles real-time ingestion without data loss
4. **Scalability**: Manages thousands of devices and billions of data points
5. **Schema Flexibility**: Adapts to changing sensor configurations seamlessly
6. **Reliability**: Maintains data integrity under all conditions
7. **Performance**: Meets all specified performance benchmarks
8. **Integration**: Works with standard IoT platforms and tools

**REQUIRED FOR SUCCESS**:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

Use `uv venv` to setup virtual environments. From within the project directory:
```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Final Deliverable Requirements

The completed implementation must include:
1. Python package with all IoT data archive functionality
2. Comprehensive pytest test suite
3. Generated pytest_results.json showing all tests passing
4. No UI components - only programmatic interfaces
5. Full compliance with IoT data handling best practices