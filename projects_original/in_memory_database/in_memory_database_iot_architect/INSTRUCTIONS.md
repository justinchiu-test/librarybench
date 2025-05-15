# EdgeDB: Time-Series Optimized In-Memory Database for IoT Systems

## Overview
A lightweight, efficient in-memory database specifically designed for edge computing devices in IoT deployments. This database specializes in time-series data management, automatic aggregation, efficient storage strategies, and data validation capabilities necessary for industrial sensor networks with limited resources.

## Persona Description
Raj designs systems for industrial IoT deployments with thousands of sensors. He needs a lightweight database that can run on edge computing devices while efficiently handling time-series sensor data.

## Key Requirements

1. **Automatic Time-Series Data Aggregation**
   - Implementation of configurable time-series downsampling with multiple resolution levels
   - Support for various aggregation functions (min, max, avg, sum, count, percentiles)
   - Automatic management of aggregation lifecycle based on data age and storage constraints
   - This feature is critical for Raj's deployments as edge devices have limited storage capacity but must retain historical sensor data at appropriate resolutions for trend analysis and anomaly detection

2. **Schema Evolution for Dynamic Sensor Types**
   - Flexible schema system that adapts to new sensor types without requiring explicit migration
   - Support for heterogeneous data types within the same time-series
   - Backward compatibility for queries across schema changes
   - Industrial IoT deployments frequently add new sensor types or modify existing ones, requiring the database to seamlessly accommodate these changes without disrupting ongoing operations

3. **Circular Buffer Storage Strategy**
   - Implementation of fixed-size circular buffer storage for historical data retention
   - Configurable retention policies based on time windows or record counts
   - Optimized memory usage for constrained edge devices
   - Edge devices must operate within strict memory limits while maintaining continuous operation over long periods, making efficient circular buffer storage essential for Raj's deployments

4. **Anomaly Detection for Sensor Validation**
   - Built-in statistical anomaly detection for sensor data validation
   - Configurable thresholds and detection algorithms for different sensor types
   - Annotation of suspect data points with confidence scores
   - Sensor data quality is critical in industrial environments, and early detection of sensor malfunctions or anomalous readings prevents cascading issues in downstream systems

5. **Edge-to-Cloud Synchronization**
   - Bandwidth-aware transmission strategies for uploading data to cloud systems
   - Prioritization mechanisms for critical data points vs. routine measurements
   - Resilient operation during connectivity interruptions with store-and-forward capabilities
   - IoT deployments typically operate in connectivity-challenged environments, requiring intelligent synchronization strategies that maximize data value while minimizing bandwidth usage

## Technical Requirements

### Testability Requirements
- Time-series aggregation must be testable with configurable time windows and functions
- Schema evolution must be verifiable through automated tests
- Circular buffer behavior must be testable under memory constraints
- Anomaly detection algorithms must be testable with known normal and abnormal patterns
- Synchronization strategies must be testable with simulated network conditions

### Performance Expectations
- System must operate efficiently on devices with as little as 256MB RAM
- Must handle at least 1,000 sensor readings per second on modest hardware
- Query performance must remain consistent as circular buffer approaches capacity
- Aggregation operations must complete in under 50ms for common window sizes
- Synchronization must use no more than 20% of available bandwidth when constrained

### Integration Points
- APIs for direct sensor data ingestion
- Query interface for local applications running on the edge device
- Synchronization protocol for communication with cloud systems
- Interface for administrative operations (configuration, monitoring)
- Integration with standard IoT protocols (MQTT, OPC UA, etc.)

### Key Constraints
- The implementation must use only Python standard library with no external dependencies
- All operations must be optimized for devices with limited CPU and memory resources
- The system must be resilient to sudden power loss without data corruption
- The database must maintain performance as it approaches storage capacity limits

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide the following core functionality:

1. **Time-Series Data Storage Engine**
   - Efficient in-memory storage optimized for time-stamped sensor readings
   - Index structures specifically designed for time-range queries
   - Memory-efficient representation of sensor values

2. **Aggregation Framework**
   - Implementation of common statistical aggregation functions
   - Time-window based aggregation with configurable resolutions
   - Automatic management of aggregated data lifecycle

3. **Anomaly Detection System**
   - Statistical models for identifying outliers in sensor data
   - Classification of anomalies by type and severity
   - Confidence scoring for detected anomalies

4. **Synchronization Engine**
   - Bandwidth-aware data transmission strategies
   - Prioritization logic for optimizing limited connectivity
   - Resilient operation during network interruptions

5. **Resource Management System**
   - Memory usage monitoring and limiting
   - Circular buffer implementation with configurable retention policies
   - Optimized performance under constrained resources

## Testing Requirements

### Key Functionalities to Verify
- Accurate storage and retrieval of time-series sensor data
- Correct aggregation results at different time resolutions
- Proper handling of schema changes as new sensor types are added
- Effective detection of anomalous sensor readings
- Efficient synchronization under varying network conditions

### Critical User Scenarios
- Continuous operation on an edge device with constrained resources
- Addition of new sensor types without disrupting existing operations
- Identification of sensor malfunctions through anomaly detection
- Recovery from network or power interruptions
- Efficient query performance for local edge applications

### Performance Benchmarks
- Ingest at least 1,000 sensor readings per second on reference hardware
- Complete common aggregation queries in under 50ms
- Maintain query performance as circular buffer approaches capacity
- Keep memory usage below 256MB for deployments with up to 1,000 sensors
- Recover from power interruption with no data loss in under 5 seconds

### Edge Cases and Error Conditions
- Behavior when memory limits are reached
- Operation during prolonged network outages
- Recovery from corrupted data states
- Handling of extremely high data ingestion rates
- Response to conflicting schema changes

### Required Test Coverage Metrics
- Minimum 90% code coverage for all modules
- 100% coverage of critical data integrity functions
- All error recovery paths must be tested
- Performance tests must cover varying load conditions
- Stress tests must verify behavior at resource limits

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

The implementation will be considered successful if:

1. It efficiently stores and manages time-series data within memory constraints
2. Aggregation functions correctly summarize data at multiple time resolutions
3. The schema system adapts to new sensor types without explicit migration
4. Anomaly detection accurately identifies suspicious sensor readings
5. Synchronization efficiently transfers data within bandwidth constraints

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup

To set up the development environment:

1. Clone the repository and navigate to the project directory
2. Create a virtual environment using:
   ```
   uv venv
   ```
3. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```
4. Install the project in development mode:
   ```
   uv pip install -e .
   ```
5. Run tests with:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

CRITICAL REMINDER: Generating and providing the pytest_results.json file is a MANDATORY requirement for project completion.