# IoT Time-Series Query Language Interpreter

## Overview
This specialized Query Language Interpreter enables IoT systems developers to efficiently query and analyze time-series measurements and device status information across distributed IoT deployments. The interpreter provides optimized time window operations, intelligent downsampling capabilities, anomaly detection filters, device hierarchy traversal, and support for intermittent connectivity, making it ideal for processing sensor data at both edge locations and central systems.

## Persona Description
Jamal builds IoT applications that process sensor data from thousands of distributed devices. He needs to query time-series measurements and device status information at the edge and in central systems.

## Key Requirements
1. **Time window operations optimized for continuous sensor data streams**: Provides specialized time window functions (sliding, tumbling, hopping, session windows) optimized for continuous sensor streams, enabling efficient analysis of recent data periods, detection of patterns within specific time spans, and comparison across different time intervals without loading full history into memory.

2. **Downsampling functions balancing query performance against result precision**: Includes intelligent downsampling algorithms that automatically reduce data resolution based on query context, preserving meaningful patterns and extremes while dramatically improving performance, critical for visualizing or analyzing long time periods of high-frequency sensor data.

3. **Anomaly filters separating unusual readings from normal sensor variations**: Incorporates statistical and machine learning-based anomaly detection that automatically identifies outliers, steps, spikes, and other unusual patterns in sensor readings, essential for distinguishing between normal sensor noise and genuine issues requiring attention.

4. **Device hierarchy traversal enabling queries across groups of related sensors**: Implements a device relationship model allowing queries to automatically aggregate or filter data across logical groupings of sensors (by location, function, system, etc.), enabling intuitive analysis from individual components up to entire subsystems without complex manual joins.

5. **Intermittent connectivity handling with partial result management and completion**: Provides mechanisms for executing queries across devices with intermittent connectivity, storing partial results, resuming interrupted operations, and completing aggregations as data becomes available, essential for distributed IoT deployments in challenging connectivity environments.

## Technical Requirements
### Testability Requirements
- Time window operations must be tested with various window types and configurations
- Downsampling algorithms must be verified for both accuracy and performance gains
- Anomaly detection must be tested against datasets with known anomalies
- Device hierarchy traversal must be validated with complex device relationship graphs
- Intermittent connectivity handling must be verified through simulated network interruptions

### Performance Expectations
- Must efficiently process time-series data at rates of at least 10,000 points per second
- Query performance should scale sub-linearly with dataset size due to optimizations
- Memory usage should remain bounded regardless of time range queried
- Edge processing must be efficient enough to run on constrained devices (e.g., Raspberry Pi)
- Response time for common queries should be under 2 seconds on typical hardware

### Integration Points
- Support for common time-series data stores and formats
- Ability to process data directly from MQTT, AMQP, and Kafka streams
- Export capabilities to visualization and analytics tools
- Integration with device management and registry systems
- Optional connectivity with cloud IoT platforms

### Key Constraints
- Must work efficiently in both edge and cloud environments
- Core functionality must operate with minimal resource consumption
- Implementation must handle unreliable network conditions gracefully
- Architecture must accommodate both batch and streaming query patterns
- Must support secure operations in potentially vulnerable IoT environments

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The core functionality of this IoT Time-Series Query Language Interpreter includes:

1. **Time-Series Query Engine**:
   - SQL-like language with extensions for time-series operations
   - Specialized parser for temporal expressions and device addressing
   - Execution planning optimized for time-series data patterns
   - Support for both batch and streaming query models

2. **Time Window Framework**:
   - Implementation of various windowing strategies (tumbling, sliding, session)
   - Optimized algorithms for window computation
   - Memory-efficient processing of large time ranges
   - Time alignment and synchronization capabilities

3. **Data Resolution Management**:
   - Intelligent downsampling algorithms preserving data characteristics
   - Adaptive resolution based on query parameters and context
   - Multi-resolution storage and retrieval strategies
   - Quality metrics for downsampled results

4. **Anomaly Detection System**:
   - Statistical algorithms for identifying outliers
   - Pattern recognition for common sensor failure modes
   - Configurable sensitivity and detection parameters
   - Context-aware anomaly significance scoring

5. **Device Management Framework**:
   - Hierarchical device relationship model
   - Efficient traversal and grouping operations
   - Metadata integration for device context
   - Query routing based on device capabilities

## Testing Requirements
### Key Functionalities to Verify
- Accuracy of time window calculations for various window types and edge cases
- Effectiveness of downsampling in preserving important data features while reducing volume
- Accuracy of anomaly detection against datasets with known anomalies
- Correct traversal of device hierarchies for complex organizational structures
- Proper handling of interrupted queries and network connectivity issues

### Critical User Scenarios
- Analyzing sensor trends across multiple devices in a production environment
- Identifying anomalous device behavior requiring maintenance
- Comparing current sensor readings with historical patterns
- Aggregating measurements across functional groups of sensors
- Managing queries in environments with unreliable connectivity

### Performance Benchmarks
- Time window operations should process at least 100,000 data points per second
- Downsampling should achieve at least 10x performance improvement for long time ranges
- Anomaly detection should process 1,000 data points per second per algorithm
- Device hierarchy traversal should handle at least 10,000 devices with 5 hierarchy levels
- System should scale to handle at least 1,000 concurrent device connections

### Edge Cases and Error Conditions
- Handling of missing or delayed data points in time series
- Behavior with highly irregular sampling intervals
- Proper management of device hierarchy changes during query execution
- Graceful degradation with extremely limited connectivity
- Appropriate treatment of time zones and daylight saving time transitions

### Required Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage for time window and downsampling functions
- All anomaly detection algorithms must have dedicated test cases
- Device hierarchy traversal must be tested with various structure types
- Connectivity handling must be tested for all failure modes

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
A successful implementation will:

1. Effectively process time-series data using optimized window operations, demonstrated through performance testing with large datasets
2. Intelligently downsample data while preserving important patterns, verified by comparing analysis results before and after downsampling
3. Accurately identify anomalies in sensor data, validated against datasets with known anomalous patterns
4. Properly traverse device hierarchies for intuitive grouped analysis, tested with complex device relationship structures
5. Successfully manage queries across intermittently connected devices, confirmed through simulated connectivity interruption scenarios

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

To set up your development environment:

```bash
# From within the project directory
uv venv
source .venv/bin/activate
uv pip install -e .
```

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY for project completion:
```bash
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```