# IoT Device Fleet Monitoring Platform

A specialized monitoring solution designed for managing large fleets of IoT devices, with a focus on battery management, firmware tracking, sensor calibration, environmental correlation, and gateway load balancing.

## Overview

This implementation of PyMonitor is tailored for industrial IoT environments, providing comprehensive monitoring of both the IoT devices themselves and the edge computing infrastructure that supports them. It focuses on power management, firmware consistency, sensor accuracy, environmental impacts, and network distribution to ensure reliable operation of IoT deployments.

## Persona Description

Amara oversees a network of IoT devices deployed across multiple industrial facilities. She needs to monitor both device health and the edge computing infrastructure supporting these devices.

## Key Requirements

1. **Battery Level Tracking**
   - Monitor power levels of battery-operated wireless devices
   - Track discharge rates and patterns across different device types and locations
   - Predict battery depletion times based on usage patterns and environmental factors
   - Alert on devices approaching critical power levels
   - Generate replacement prioritization lists for maintenance teams
   - This is critical because battery failure is a primary cause of IoT device outages, and proactive replacement planning minimizes downtime in industrial settings.

2. **Firmware Version Monitoring**
   - Track firmware versions across the entire device fleet
   - Identify devices with outdated, vulnerable, or incompatible firmware
   - Monitor firmware update progress and success/failure rates
   - Detect unauthorized or unexpected firmware changes
   - Generate firmware consistency reports for compliance and security
   - This is critical because firmware consistency ensures proper device function and security, while inconsistent firmware versions can cause compatibility issues and security vulnerabilities.

3. **Sensor Calibration Drift Detection**
   - Monitor sensor readings for signs of calibration drift
   - Compare readings across similar sensors to identify outliers
   - Track calibration history and predict recalibration needs
   - Correlate environmental factors with calibration stability
   - Generate calibration verification and servicing schedules
   - This is critical because sensor accuracy directly impacts data quality and operational decisions, and undetected calibration drift can lead to faulty data analysis and incorrect actions.

4. **Environmental Condition Correlation**
   - Track environmental factors (temperature, humidity, vibration) affecting devices
   - Correlate environmental conditions with device performance and failures
   - Identify optimal and problematic operating conditions
   - Predict maintenance needs based on environmental stress
   - Generate environment optimization recommendations
   - This is critical because IoT devices in industrial settings are often deployed in harsh conditions that can significantly impact their lifespan and reliability.

5. **Gateway Load Balancing Monitoring**
   - Track device connection distribution across access points and gateways
   - Monitor gateway performance metrics under varying connection loads
   - Detect imbalances and potential bottlenecks in the network
   - Analyze connection patterns and recommend optimal distribution
   - Alert on gateway overloading or potential failures
   - This is critical because network gateway capacity and distribution directly impact data transmission reliability, and overloaded gateways can create single points of failure for large numbers of devices.

## Technical Requirements

### Testability Requirements
- All IoT monitoring components must be testable with simulated device data
- Battery level tracking must be verifiable with synthetic discharge patterns
- Firmware monitoring must be testable with mock version data
- Calibration drift detection must work with simulated sensor readings
- Environmental correlation must be testable with synthetic environmental data
- Gateway load testing must support simulated connection patterns

### Performance Expectations
- Support for monitoring at least 10,000 IoT devices concurrently
- Process metrics from at least 1,000 device readings per second
- Battery predictions with at least 85% accuracy for 30-day forecasts
- Calibration drift detection with sensitivity to 2% deviation from expected values
- Environmental correlation analysis completing within 5 minutes of data receipt
- Response time for device queries under 2 seconds even with large device fleets

### Integration Points
- IoT device management platforms and protocols (MQTT, CoAP, etc.)
- Gateway and access point management interfaces
- Device firmware management systems
- Environmental monitoring systems
- Maintenance and ticketing systems
- IoT data storage and analysis platforms

### Key Constraints
- Must support heterogeneous device types from multiple manufacturers
- Cannot require significant device-side processing or storage
- Must operate with minimal bandwidth consumption
- Should function with intermittent device connectivity
- Must scale to support growing device fleets without redesign
- Cannot rely on proprietary vendor-specific management interfaces

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system should consist of these core modules:

1. **Power Management Module**
   - Battery level data collection and normalization
   - Discharge rate analysis and pattern recognition
   - Predictive algorithms for depletion forecasting
   - Criticality assessment and alerting
   - Replacement prioritization and scheduling

2. **Firmware Management System**
   - Version tracking and inventory management
   - Update monitoring and verification
   - Anomaly detection for unexpected changes
   - Consistency analysis across device groups
   - Vulnerability tracking and security assessment

3. **Sensor Quality Monitor**
   - Calibration drift detection algorithms
   - Cross-sensor comparison and outlier detection
   - Historical calibration tracking
   - Maintenance scheduling optimization
   - Degradation trend analysis

4. **Environmental Analysis Engine**
   - Environmental data collection and correlation
   - Performance impact assessment
   - Failure prediction based on conditions
   - Operating environment optimization
   - Stress factor identification and mitigation

5. **Network Distribution Analyzer**
   - Gateway performance and capacity monitoring
   - Connection distribution tracking
   - Load balancing assessment
   - Bottleneck identification
   - Optimization recommendation engine

## Testing Requirements

### Key Functionalities to Verify
- Accurate battery level tracking and depletion prediction
- Reliable firmware version monitoring and consistency checking
- Precise sensor calibration drift detection
- Effective correlation of environmental conditions with performance
- Accurate gateway load distribution monitoring

### Critical User Scenarios
- Planning battery replacement maintenance schedules
- Ensuring firmware consistency across device deployments
- Identifying sensors requiring recalibration
- Understanding environmental impacts on device performance
- Optimizing gateway load distribution

### Performance Benchmarks
- Battery level prediction accuracy within 15% for 30-day forecasts
- Firmware inconsistency detection within 1 hour of occurrence
- Calibration drift detection sensitivity to 2% deviation
- Environmental correlation analysis for 10,000 devices in under 5 minutes
- Gateway load analysis for networks with 500+ access points in under 2 minutes

### Edge Cases and Error Conditions
- Handling devices with unreliable or intermittent reporting
- Managing environmental data gaps or sensor failures
- Accommodating various battery types and discharge patterns
- Adapting to new firmware versions and update methods
- Handling gateway failures and network reconfiguration

### Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of battery prediction algorithms
- 100% coverage of firmware version comparison logic
- 95% coverage of calibration drift detection
- 90% coverage of environmental correlation functions
- 95% coverage of gateway load analysis

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

A successful implementation will satisfy the following requirements:

1. **Effective Power Management**
   - Accurate tracking of battery levels across device fleet
   - Reliable prediction of battery depletion times
   - Prioritized replacement scheduling that minimizes downtime

2. **Consistent Firmware Control**
   - Complete visibility of firmware versions across the fleet
   - Accurate detection of version inconsistencies
   - Reliable monitoring of update processes

3. **Precise Calibration Management**
   - Accurate detection of sensor calibration drift
   - Reliable identification of sensors needing recalibration
   - Optimized maintenance scheduling based on calibration needs

4. **Insightful Environmental Analysis**
   - Clear correlation between environmental conditions and device performance
   - Accurate prediction of environmentally-induced failures
   - Actionable recommendations for environmental optimization

5. **Balanced Network Distribution**
   - Complete visibility of device distribution across gateways
   - Accurate identification of network bottlenecks
   - Effective load balancing recommendations

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Environment Setup

To set up your development environment:

```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate

# Install the project in development mode
uv pip install -e .

# Install testing dependencies
uv pip install pytest pytest-json-report
```

REMINDER: Running tests with pytest-json-report is MANDATORY for project completion:
```bash
pytest --json-report --json-report-file=pytest_results.json
```