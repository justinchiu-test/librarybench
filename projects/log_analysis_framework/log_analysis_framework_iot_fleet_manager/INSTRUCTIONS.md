# IoT Fleet Log Analysis Framework

A specialized log analysis framework designed for IoT fleet managers to monitor device health, connectivity, and performance across distributed industrial deployments.

## Overview

This project implements a comprehensive log analysis system tailored for IoT fleet management in industrial environments. It provides device lifecycle tracking, connectivity pattern analysis, power consumption monitoring, sensor calibration drift detection, and geospatial deployment visualization to help manage a diverse ecosystem of connected devices.

## Persona Description

Carlos oversees a network of industrial IoT devices deployed across manufacturing facilities. He needs to monitor device health, update status, and troubleshoot connectivity issues across a diverse hardware ecosystem.

## Key Requirements

1. **Device Lifecycle Tracking**
   - Implement functionality to show firmware versions and update history across the fleet
   - Critical for Carlos to maintain device software currency and security
   - Must track current firmware version, available updates, and update history for each device
   - Should identify devices requiring urgent updates due to security vulnerabilities
   - Must track update success/failure rates and correlate with device models or deployment environments

2. **Connectivity Pattern Analysis**
   - Create a system to identify environmental factors affecting reliability
   - Essential for Carlos to understand and mitigate connectivity challenges in industrial settings
   - Should detect patterns in connectivity issues (time of day, proximity to machinery, etc.)
   - Must identify intermittent vs. persistent connectivity problems
   - Should recognize communication protocol-specific issues (WiFi, Cellular, LoRaWAN, etc.)

3. **Power Consumption Anomaly Detection**
   - Develop monitoring for energy usage patterns to highlight potential hardware failures
   - Necessary for Carlos to proactively identify devices with battery or power issues
   - Should establish baseline power consumption for different device types and operations
   - Must detect sudden or gradual changes in power usage that indicate potential problems
   - Should predict battery replacement needs before device failure

4. **Sensor Calibration Drift Monitoring**
   - Build analytics to compare readings against expected baselines
   - Important for Carlos to ensure data accuracy from industrial sensors
   - Should detect when sensor readings drift from expected values or peer devices
   - Must suggest recalibration needs based on drift patterns
   - Should differentiate between normal sensor aging and potential failures

5. **Geospatial Deployment Visualization**
   - Implement mapping of device status across physical locations
   - Vital for Carlos to understand the geographic distribution of device health and issues
   - Should visualize device status, connectivity strength, and alerts on facility maps
   - Must identify location-based patterns in device performance or failures
   - Should support different levels of detail (region, facility, production line, etc.)

## Technical Requirements

### Testability Requirements
- All functionality must be testable via pytest with appropriate fixtures and mocks
- Tests must validate accurate parsing of diverse IoT device logs
- Test coverage should exceed 85% for all modules
- Performance tests must simulate high-device-count scenarios (10,000+ devices)
- Tests should verify analysis algorithms with synthetic time-series data

### Performance Expectations
- Must process logs from 10,000+ concurrently connected devices
- Should handle devices reporting at different frequencies (from seconds to hours)
- Analysis operations should complete within seconds even with large historical datasets
- Should support both real-time monitoring and historical batch analysis
- Must handle intermittent connectivity and delayed log delivery

### Integration Points
- Compatible with major IoT protocols (MQTT, CoAP, LwM2M, etc.)
- Support for various data formats (JSON, CBOR, Protobuf, etc.)
- Integration with device management platforms
- Support for geospatial data standards
- Optional integration with notification systems and maintenance workflows

### Key Constraints
- Must handle heterogeneous device types with different capabilities and log formats
- Should operate with limited bandwidth and intermittent connectivity
- Implementation should minimize on-device resource requirements
- Must support offline analysis when field connectivity is limited
- Should handle time synchronization challenges across distributed devices

## Core Functionality

The system must implement these core capabilities:

1. **Device Log Collector**
   - Ingest logs from various IoT protocols and formats
   - Handle batched uploads from intermittently connected devices
   - Normalize timestamps and device identifiers
   - Manage data volume through intelligent filtering

2. **Firmware Management Tracker**
   - Monitor current firmware versions across the fleet
   - Track update histories and outcomes
   - Identify devices with outdated or vulnerable firmware
   - Analyze update success rates and failure patterns

3. **Connectivity Analyzer**
   - Measure connection quality and reliability
   - Detect patterns in connectivity failures
   - Correlate environmental factors with connection issues
   - Predict connectivity problems before complete failure

4. **Resource Utilization Monitor**
   - Track power consumption patterns
   - Detect anomalies in resource usage
   - Predict battery life and maintenance needs
   - Identify resource-intensive operations

5. **Sensor Analytics Engine**
   - Compare sensor readings against baseline values
   - Detect calibration drift and anomalies
   - Correlate readings across similar sensors
   - Recommend maintenance and recalibration actions

## Testing Requirements

### Key Functionalities to Verify

- **Firmware Tracking**: Verify accurate monitoring of firmware versions and update history
- **Connectivity Analysis**: Ensure correct identification of connectivity patterns and issues
- **Power Monitoring**: Validate detection of power consumption anomalies
- **Calibration Tracking**: Confirm accurate detection of sensor calibration drift
- **Geospatial Visualization**: Verify correct mapping of device status to physical locations

### Critical User Scenarios

- Monitoring a firmware update rollout across 1,000+ devices
- Troubleshooting connectivity issues affecting devices in a specific factory area
- Identifying devices with abnormal power consumption before battery failure
- Detecting sensors requiring recalibration based on drift patterns
- Analyzing the geographic distribution of device health issues across multiple facilities

### Performance Benchmarks

- Process logs from 10,000 devices reporting every 5 minutes in real-time
- Complete firmware version analysis across entire fleet in under 30 seconds
- Analyze 30 days of connectivity data for pattern detection in under 2 minutes
- Detect power consumption anomalies within 10 minutes of pattern emergence
- Generate calibration drift reports for 1,000 sensors in under 1 minute
- Render geospatial visualizations of 5,000+ devices in under 5 seconds

### Edge Cases and Error Handling

- Handle devices with irregular reporting intervals or missed reports
- Process logs from new device types with unknown or changed formats
- Manage data from devices with incorrect or drifting timestamps
- Handle devices transitioning between different network technologies
- Process partial or corrupted logs from devices with connectivity issues

### Test Coverage Requirements

- 90% coverage for device log parsing and normalization
- 85% coverage for firmware version tracking
- 90% coverage for connectivity pattern analysis
- 90% coverage for power consumption anomaly detection
- 85% coverage for sensor calibration drift algorithms
- 85% coverage for geospatial mapping functions
- 85% overall code coverage

## Success Criteria

The implementation meets Carlos's needs when it can:

1. Accurately track firmware versions and update history for 100% of managed devices
2. Identify connectivity pattern issues and their root causes with >90% accuracy
3. Detect power consumption anomalies at least 24 hours before they cause device failure
4. Identify sensors requiring calibration with >95% accuracy and <5% false positives
5. Visualize device status across different geographic levels (region, facility, zone)
6. Process logs from 10,000+ devices without performance degradation
7. Reduce mean time to resolution for device issues by at least 60%

## Getting Started

To set up your development environment and start working on this project:

1. Initialize a new Python library project using uv:
   ```
   uv init --lib
   ```

2. Install dependencies:
   ```
   uv sync
   ```

3. Run tests:
   ```
   uv run pytest
   ```

4. Run specific tests:
   ```
   uv run pytest tests/test_device_connectivity.py
   ```

5. Run your code:
   ```
   uv run python examples/analyze_device_logs.py
   ```

Remember that all functionality should be implemented as importable Python modules with well-defined APIs, not as user-facing applications.