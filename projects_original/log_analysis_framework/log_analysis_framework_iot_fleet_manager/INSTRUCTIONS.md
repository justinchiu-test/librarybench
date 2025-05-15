# IoT Fleet Monitoring Log Analysis Framework

## Overview
A specialized log analysis framework designed for managers overseeing industrial IoT device networks. This system monitors device health, tracks firmware updates, analyzes connectivity patterns, detects power anomalies, and provides geospatial visualizations to ensure reliable operation of distributed IoT deployments.

## Persona Description
Carlos oversees a network of industrial IoT devices deployed across manufacturing facilities. He needs to monitor device health, update status, and troubleshoot connectivity issues across a diverse hardware ecosystem.

## Key Requirements

1. **Device Lifecycle Tracking**
   - Monitoring of firmware versions and update history across the entire device fleet
   - Status tracking for deployment, activation, maintenance, and decommissioning stages
   - Failure rate analysis by device model, firmware version, and deployment environment
   - This feature is critical because industrial IoT deployments involve devices with varying lifespans and update cycles that must be actively managed to ensure operational reliability.

2. **Connectivity Pattern Analysis**
   - Identification of environmental factors affecting device reliability
   - Detection of interference patterns and connectivity degradation
   - Network performance analysis by location, time, and environmental conditions
   - This feature is essential because connectivity issues in industrial settings can be caused by various environmental factors that are difficult to diagnose without systematic pattern analysis.

3. **Power Consumption Anomaly Detection**
   - Monitoring for unusual power usage patterns that might indicate hardware failures
   - Battery life prediction for remote devices
   - Correlation between power consumption and operational parameters
   - This feature is vital because power anomalies often precede device failures, and early detection can prevent downtime in critical manufacturing processes.

4. **Sensor Calibration Drift Monitoring**
   - Comparison of sensor readings against expected baselines
   - Statistical analysis of calibration stability over time
   - Automated identification of sensors requiring recalibration
   - This feature is important because inaccurate sensor readings due to calibration drift can lead to quality issues in manufacturing processes and inaccurate monitoring of critical conditions.

5. **Geospatial Deployment Visualization**
   - Mapping of device status across physical locations
   - Spatial correlation of issues affecting multiple devices in proximity
   - Environmental impact analysis based on geographic patterns
   - This feature is necessary because understanding the spatial distribution of device issues can reveal location-specific problems affecting multiple devices that wouldn't be apparent when looking at individual device logs.

## Technical Requirements

### Testability Requirements
- All device analysis algorithms must be testable with synthetic device logs and telemetry data
- Connectivity analysis must be verifiable with simulated network condition datasets
- Power consumption anomaly detection must demonstrate statistical validity
- Sensor drift detection algorithms must be testable with controlled degradation patterns

### Performance Expectations
- Process telemetry from at least 10,000 devices reporting at 1-minute intervals
- Support historical analysis of at least 1 year of device logs for trend analysis
- Generate fleet-wide reports and visualizations in under 60 seconds
- Perform real-time anomaly detection with alerting in under 30 seconds from data receipt

### Integration Points
- Support for major IoT communication protocols (MQTT, CoAP, etc.)
- Integration with device management platforms and firmware update systems
- Support for various sensor data formats and telemetry schemas
- Export capabilities for maintenance management systems

### Key Constraints
- Must operate with minimal bandwidth consumption from remote devices
- Should handle intermittent connectivity from devices in challenging environments
- Must process heterogeneous data from diverse device types and manufacturers
- Should function with limited processing power on edge devices

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The core functionality of the IoT Fleet Monitoring Log Analysis Framework includes:

1. **Device Data Collection and Management**
   - Telemetry ingestion from diverse IoT devices
   - Normalization of heterogeneous data formats
   - Efficient storage and indexing of device logs
   - Historical data retention and aggregation

2. **Fleet Analysis Engine**
   - Device lifecycle state tracking and management
   - Firmware version monitoring and update verification
   - Batch comparison of similar devices under different conditions
   - Fleet-wide health scoring and trend analysis

3. **Connectivity and Communication Analysis**
   - Network performance measurement and baseline establishment
   - Interference detection and signal quality analysis
   - Communication pattern modeling and anomaly detection
   - Protocol efficiency analysis and optimization

4. **Operational Diagnostics**
   - Power consumption profiling and anomaly detection
   - Sensor calibration analysis and drift detection
   - Environmental impact correlation
   - Predictive maintenance modeling

5. **Geospatial Analytics**
   - Location-based grouping and analysis
   - Spatial correlation of device issues
   - Environmental factor mapping
   - Regional performance comparison

## Testing Requirements

### Key Functionalities to Verify
- Accurate tracking of device lifecycle states and firmware versions
- Reliable detection of connectivity patterns and interference factors
- Precise identification of power consumption anomalies
- Accurate measurement of sensor calibration drift
- Effective visualization and analysis of geospatial device patterns

### Critical User Scenarios
- Monitoring a large-scale firmware update across thousands of devices
- Troubleshooting connectivity issues in a manufacturing environment with high EMI
- Identifying devices at risk of failure due to power consumption anomalies
- Detecting and addressing sensor calibration drift before it affects production
- Analyzing regional performance variations across multiple manufacturing sites

### Performance Benchmarks
- Device data processing: Minimum 10,000 device updates per minute
- Historical analysis: Query and analyze 1 year of data for 1,000 devices in under 60 seconds
- Anomaly detection: Identify critical anomalies within 30 seconds of data receipt
- Geospatial analysis: Generate location-based reports for 5,000 devices in under 30 seconds
- Predictive analytics: Calculate failure probabilities for 10,000 devices in under 5 minutes

### Edge Cases and Error Conditions
- Handling devices with irregular reporting patterns
- Processing corrupted or partial telemetry data
- Managing devices with incorrect time settings
- Analyzing devices operating outside design parameters
- Detecting tampered or compromised devices

### Required Test Coverage Metrics
- Minimum 90% line coverage across all modules
- 100% coverage of anomaly detection and lifecycle tracking logic
- Comprehensive testing of different device types and communication protocols
- Full testing of geospatial analysis with various deployment patterns

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

1. It accurately tracks device lifecycle stages and firmware versions across the fleet
2. It reliably identifies connectivity patterns and environmental factors affecting performance
3. It precisely detects power consumption anomalies that indicate potential device failures
4. It accurately monitors sensor calibration drift against expected baselines
5. It effectively visualizes and analyzes geospatial patterns in device deployment and issues
6. It meets performance benchmarks for processing telemetry from thousands of devices
7. It provides actionable insights for fleet management and maintenance prioritization
8. It offers a well-documented API for integration with IoT management systems

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Development Setup

1. Set up a virtual environment using `uv venv`
2. From within the project directory, activate the environment with `source .venv/bin/activate`
3. Install the project with `uv pip install -e .`
4. Install test dependencies with `uv pip install pytest pytest-json-report`

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```