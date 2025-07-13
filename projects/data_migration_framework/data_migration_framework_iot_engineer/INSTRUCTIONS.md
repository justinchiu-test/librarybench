# PyMigrate IoT Edge-to-Cloud Migration Framework

## Overview
A specialized data migration framework designed for IoT engineers migrating time-series sensor data from edge devices to cloud storage. This implementation handles intermittent connectivity, provides intelligent buffering strategies, and ensures reliable data delivery from resource-constrained edge environments to scalable cloud platforms.

## Persona Description
An IoT engineer migrating time-series sensor data from edge devices to cloud storage who needs to handle intermittent connectivity and data buffering. He requires resilient migration strategies for unreliable networks.

## Key Requirements

1. **Edge-to-cloud migration with offline buffering capabilities**
   - Essential for handling unreliable network conditions common in IoT deployments. Implements intelligent local buffering that prioritizes critical data, manages storage constraints on edge devices, and ensures eventual delivery when connectivity is restored.

2. **Sensor data deduplication with timestamp reconciliation**
   - Prevents duplicate data from multiple retry attempts while reconciling timestamps across devices with clock drift. Critical for maintaining data integrity and preventing storage waste from redundant sensor readings.

3. **Adaptive retry strategies for network failures**
   - Dynamically adjusts retry behavior based on network conditions and failure patterns. Implements exponential backoff, jitter, and circuit breaker patterns to optimize delivery success while minimizing battery and bandwidth consumption.

4. **Data aggregation rules for bandwidth optimization**
   - Reduces bandwidth usage by intelligently aggregating sensor data at the edge. Supports time-based, count-based, and condition-based aggregation with configurable rules that preserve data fidelity while minimizing transmission costs.

5. **Device fleet migration coordination with rolling updates**
   - Orchestrates migrations across thousands of devices without overwhelming cloud infrastructure. Implements wave-based rollouts, monitors device health, and provides rollback capabilities for fleet-wide configuration changes.

## Technical Requirements

### Testability Requirements
- All components must be testable via pytest without manual intervention
- Simulated edge device constraints (CPU, memory, storage)
- Network condition simulation (latency, packet loss, disconnection)
- Mock IoT protocols and cloud endpoints

### Performance Expectations
- Buffer management with <1MB memory footprint per device
- Support for 100,000+ devices in fleet
- Data compression achieving 70%+ reduction
- Retry logic with <1% CPU overhead on edge devices

### Integration Points
- IoT protocols (MQTT, CoAP, AMQP) for data transport
- Time-series databases (InfluxDB, TimescaleDB, AWS Timestream)
- Edge computing frameworks (AWS Greengrass, Azure IoT Edge)
- Device management platforms for fleet coordination

### Key Constraints
- Minimal resource usage on constrained devices
- Operation in disconnected environments
- Battery-efficient retry strategies
- Bandwidth-conscious data transmission

**IMPORTANT**: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The framework must provide:

1. **Offline Buffer Manager**: Implements circular buffer with priority queuing, manages storage allocation on constrained devices, provides data persistence across power cycles, and supports configurable retention policies

2. **Deduplication Engine**: Generates efficient fingerprints for sensor data, maintains sliding window of recent transmissions, handles timestamp normalization across devices, and provides conflict resolution for concurrent readings

3. **Adaptive Retry Controller**: Monitors network quality indicators, implements smart backoff algorithms, provides circuit breaker functionality, and optimizes retry timing for battery life

4. **Data Aggregation Pipeline**: Supports multiple aggregation functions (min, max, avg, sum), implements windowing strategies for time-series data, provides downsampling capabilities, and maintains aggregation metadata

5. **Fleet Coordination Service**: Manages device group definitions, implements rolling update strategies, monitors migration progress per device, and provides fleet-wide health metrics

## Testing Requirements

### Key Functionalities to Verify
- Offline buffering preserves data during extended disconnections
- Deduplication correctly identifies redundant sensor readings
- Retry strategies adapt to various network conditions
- Aggregation maintains statistical accuracy
- Fleet coordination scales to large device populations

### Critical User Scenarios
- Migrating data from remote weather stations with daily connectivity
- Handling industrial sensor bursts during network congestion
- Coordinating firmware updates across global device fleet
- Recovering from extended cloud service outages
- Optimizing costs for cellular IoT deployments

### Performance Benchmarks
- Buffer 24 hours of data using <10MB storage
- Achieve 90%+ deduplication accuracy
- Deliver 95% of data within 3 retry attempts
- Reduce bandwidth by 75% through aggregation
- Coordinate 10,000 device updates in <1 hour

### Edge Cases and Error Conditions
- Device storage exhaustion during offline period
- Clock synchronization failures across devices
- Corrupted data in persistent buffers
- Network partitions isolating device groups
- Cloud API rate limiting during bulk uploads

### Required Test Coverage
- Minimum 90% code coverage with pytest
- Edge device resource constraint tests
- Network failure simulation tests
- Data integrity validation across migrations
- Scale tests for fleet operations

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

The implementation is successful when:

1. **All tests pass** when run with pytest, with 90%+ code coverage
2. **A valid pytest_results.json file** is generated showing all tests passing
3. **Offline buffering** handles 24+ hour disconnections without data loss
4. **Deduplication** achieves 90%+ accuracy in identifying duplicates
5. **Retry strategies** deliver 95%+ of data within resource constraints
6. **Aggregation** reduces bandwidth usage by 70%+ while preserving insights
7. **Fleet coordination** manages 10,000+ devices efficiently

**REQUIRED FOR SUCCESS**:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

To set up the development environment:

```bash
cd /path/to/data_migration_framework_iot_engineer
uv venv
source .venv/bin/activate
uv pip install -e .
```

Install the project and run tests:

```bash
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```

**REMINDER**: The pytest_results.json file is MANDATORY and must be included to demonstrate that all tests pass successfully.