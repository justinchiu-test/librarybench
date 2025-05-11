# Industrial IoT Data Stream Processing Pipeline

## Overview
A scalable data processing framework designed to ingest, process, and analyze data streams from millions of industrial IoT sensors. The system provides efficient resource utilization, adaptive processing based on data patterns, and specialized handling for diverse industrial sensor protocols.

## Persona Description
Carlos designs systems that ingest data from millions of connected industrial sensors for a manufacturing analytics platform. His primary goal is to scale the data processing horizontally while ensuring efficient resource utilization across his cloud infrastructure.

## Key Requirements
1. **Dynamic worker allocation based on sensor activation patterns**: Implement a system that automatically scales processing resources up and down based on temporal patterns of sensor activity across different manufacturing zones. This is critical for efficient resource utilization in facilities that operate with predictable shift patterns but unpredictable sensor activity density.

2. **Time-series compression for efficient storage of periodic signals**: Create specialized encoding and compression algorithms tailored to industrial time-series data, particularly for sensors that report at fixed intervals with predictable value ranges. This capability dramatically reduces storage costs and network bandwidth while preserving analytical accuracy for terabytes of daily sensor data.

3. **Device-specific protocol adapters with plug-in architecture**: Design a flexible adapter framework that supports the diverse communication protocols used by industrial sensors (Modbus, OPC-UA, MQTT, proprietary protocols) through a consistent interface. This extensibility is essential for integrating the wide variety of equipment found in modern factories without custom code for each device type.

4. **Batch/stream hybrid processing for different data velocity requirements**: Develop a unified processing architecture that intelligently routes data to either real-time stream processing (for critical operational metrics) or batch aggregation (for long-term trend analysis) based on data characteristics and business value. This dual-mode capability addresses the diverse analytical needs across operational monitoring and strategic planning.

5. **Sensor health monitoring with anomalous transmission detection**: Implement capabilities that automatically detect irregular sensor behavior including intermittent connections, calibration drift, and unusual reporting patterns that might indicate equipment failure. This proactive diagnosis prevents data quality issues that could impact manufacturing decisions and minimizes maintenance costs through early detection.

## Technical Requirements
- **Testability Requirements**:
  - Must support simulation of thousands of virtual sensors with configurable behaviors
  - Needs reproducible testing with controlled sensor transmission patterns
  - Requires validation against historical device behavior profiles
  - Must support fault injection testing for communications and sensor failures
  - Needs verification of functional behavior under varying load levels

- **Performance Expectations**:
  - Ability to process at least 500,000 sensor readings per second
  - Support for at least 1 million concurrently connected devices
  - Horizontal scaling to handle 2x capacity increase within 5 minutes
  - Maximum latency of 5 seconds for real-time alerts
  - Storage efficiency achieving at least 10:1 compression ratio for time-series data

- **Integration Points**:
  - Industrial protocol gateways and edge devices
  - Time-series databases for historical data storage
  - Alerting and notification systems
  - Equipment management and asset tracking systems
  - Analytics and reporting platforms

- **Key Constraints**:
  - Must operate within a containerized cloud infrastructure
  - Processing latency must not exceed 5 seconds for critical alerts
  - Implementation must be resilient to network interruptions
  - System must handle sensor clock synchronization issues
  - Storage solution must be cost-optimized for massive data volumes

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The system must provide a framework for IoT data stream processing that:

1. Ingests data from diverse industrial sensors with protocol-specific adapters
2. Normalizes varied data formats into consistent internal representations
3. Implements configurable processing pipelines that support:
   - Dynamic resource allocation based on incoming data patterns
   - Intelligent routing to real-time or batch processing paths
   - Efficient compression for time-series data storage
   - Anomaly detection for sensor health monitoring
   - Aggregation and statistical analysis of sensor trends
4. Manages cloud resource allocation to optimize costs
5. Provides monitoring and alerting for system health and sensor status
6. Offers a plugin architecture for custom protocol and processing components
7. Maintains metadata about sensor types, locations, and expected behaviors

The implementation should emphasize horizontal scalability, resource efficiency, and the ability to handle highly heterogeneous data sources through a consistent processing framework.

## Testing Requirements
- **Key Functionalities to Verify**:
  - Correct handling of multiple industrial protocols and data formats
  - Proper implementation of dynamic resource allocation algorithms
  - Effectiveness of time-series compression algorithms
  - Accuracy of sensor health anomaly detection
  - Performance under various load scenarios
  - Proper functioning of the batch/stream hybrid processing system

- **Critical User Scenarios**:
  - System behavior during manufacturing shift transitions with sudden sensor activity spikes
  - Performance during facility-wide process changes affecting thousands of sensors
  - Handling of communications interruptions and delayed data arrival
  - Response to sensor firmware updates across a device fleet
  - Behavior under simulated sensor failure conditions

- **Performance Benchmarks**:
  - Ingestion rate of 500,000+ sensor readings per second
  - Support for 1 million+ connected devices
  - Compression ratio of at least 10:1 for typical industrial sensor data
  - Resource utilization scaling proportional to workload within 10% margin
  - Alert delivery for critical conditions within 5 seconds

- **Edge Cases and Error Conditions**:
  - Handling of corrupted sensor data transmissions
  - Recovery from network partitions and connectivity loss
  - Behavior with severely clock-skewed device timestamps
  - Processing of backlogged data after system recovery
  - Response to malformed or non-compliant protocol messages

- **Required Test Coverage Metrics**:
  - 100% coverage of protocol adapter interfaces
  - >90% line coverage for all production code
  - 100% coverage of error handling paths
  - Integration tests for all supported sensor protocols
  - Load tests verifying performance at 2x expected production scale

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

1. Efficient processing of data from millions of industrial sensors with optimized resource utilization
2. Intelligent allocation of computing resources based on sensor activity patterns
3. Effective compression of time-series data with minimal information loss
4. Flexible support for diverse industrial communication protocols
5. Reliable detection of sensor health issues and anomalous behavior
6. Appropriate handling of both real-time and batch processing needs
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