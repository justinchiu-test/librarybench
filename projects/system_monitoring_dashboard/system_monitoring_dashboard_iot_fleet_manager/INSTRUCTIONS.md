# IoT Device Fleet Monitoring System

A comprehensive monitoring solution designed for large-scale IoT device deployments across multiple industrial facilities, focusing on device health, power management, firmware consistency, and environmental impacts.

## Overview

The IoT Device Fleet Monitoring System is a specialized implementation of the PyMonitor system tailored for managing networks of IoT devices and their supporting edge infrastructure. It provides detailed visibility into battery levels, firmware versions, sensor calibration, environmental conditions, and connection distribution to ensure reliable operation of distributed IoT deployments.

## Persona Description

Amara oversees a network of IoT devices deployed across multiple industrial facilities. She needs to monitor both device health and the edge computing infrastructure supporting these devices.

## Key Requirements

1. **Battery Level Tracking** - Implement functionality to monitor and forecast power levels for wireless IoT devices. This is critical for Amara because unexpected power failures in industrial IoT devices can cause safety issues, production downtime, and require expensive emergency maintenance visits to remote locations.

2. **Firmware Version Monitoring** - Develop a system to track firmware versions across the device fleet and identify inconsistencies. Amara needs this because maintaining consistent firmware across thousands of devices is essential for security, feature parity, and troubleshooting, and manual tracking is impractical at scale.

3. **Sensor Calibration Drift Detection** - Create capabilities to identify when sensors begin producing readings that deviate from expected patterns. This feature is essential because sensor calibration drift can lead to inaccurate data, false alarms, or missed critical conditions in industrial environments where precision is vital.

4. **Environmental Condition Correlation** - Implement analytics to show how environmental factors like temperature affect device performance. This is crucial for Amara because extreme industrial environments can impact device reliability and data accuracy, and understanding these correlations helps optimize device placement and maintenance schedules.

5. **Gateway Load Balancing Monitoring** - Develop functionality to track the distribution of device connections across access points and gateways. Amara requires this because imbalanced connection distributions can overload some gateways while underutilizing others, leading to communication bottlenecks, increased latency, and potential data loss.

## Technical Requirements

### Testability Requirements
- All IoT monitoring components must be testable with pytest
- Battery level prediction algorithms must be verifiable with historical data
- Firmware tracking must be testable with simulated version information
- Calibration drift detection must validate against known drift patterns
- Gateway load analysis must be verifiable with synthetic connection data

### Performance Expectations
- Minimal bandwidth usage for communication with constrained devices
- Support for monitoring tens of thousands of devices simultaneously
- Battery forecasting that predicts depletion at least 2 weeks in advance
- Sensor drift detection within 48 hours of beginning deviation
- Real-time gateway load visualization updated every 60 seconds

### Integration Points
- IoT device management platforms and protocols (MQTT, CoAP, etc.)
- Battery management systems and power monitoring APIs
- Firmware management and over-the-air update systems
- Sensor data collection and calibration frameworks
- Gateway and access point management interfaces

### Key Constraints
- Must operate with extremely bandwidth-constrained devices
- Should minimize power impact on battery-operated devices
- Must scale to tens of thousands of distributed devices
- Should accommodate diverse device types, capabilities, and protocols
- Must function across multiple physical locations with varying connectivity

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The IoT Device Fleet Monitoring System must implement the following core functionality:

1. **Power Management**
   - Battery level monitoring and historical tracking
   - Discharge rate analysis and pattern recognition
   - Predictive depletion forecasting
   - Anomalous power consumption detection
   - Maintenance scheduling optimization based on power status

2. **Firmware Lifecycle Management**
   - Version tracking across heterogeneous device types
   - Update status and distribution visualization
   - Consistency verification across device groups
   - Rollback and failure detection
   - Deployment success rate analysis

3. **Sensor Performance Analysis**
   - Baseline establishment for expected sensor readings
   - Drift detection using statistical methods
   - Cross-sensor correlation and verification
   - Recalibration requirement identification
   - Measurement accuracy confidence scoring

4. **Environmental Impact Assessment**
   - Temperature, humidity, and other environmental tracking
   - Correlation between conditions and device performance
   - Extreme condition alerting and impact prediction
   - Seasonal pattern analysis for proactive management
   - Device placement optimization recommendations

5. **Network Infrastructure Optimization**
   - Gateway connection distribution tracking
   - Load imbalance detection and alerting
   - Communication pattern analysis
   - Bottleneck identification and resolution recommendations
   - Failover and redundancy verification

## Testing Requirements

The implementation must include comprehensive tests that validate:

### Key Functionalities Verification
- Accuracy of battery level prediction algorithms
- Reliability of firmware version tracking and reporting
- Precision of sensor calibration drift detection methods
- Effectiveness of environmental condition correlation
- Correctness of gateway load distribution analysis

### Critical User Scenarios
- Proactively replacing batteries before device failure
- Planning and tracking firmware updates across thousands of devices
- Identifying sensors requiring recalibration or replacement
- Adapting monitoring and maintenance based on environmental forecasts
- Rebalancing device connections to optimize gateway performance

### Performance Benchmarks
- Battery prediction accuracy compared to actual depletion times
- Time to detect and report firmware inconsistencies
- Sensitivity and specificity of calibration drift detection
- Statistical significance of environmental correlation analysis
- Response time for gateway load distribution visualization

### Edge Cases and Error Handling
- Behavior with intermittently connected devices
- Handling of devices with limited or no power reporting
- Response to sudden environmental changes
- Management of devices that cannot receive firmware updates
- Recovery after gateway or connection failures

### Required Test Coverage
- 90% code coverage for core monitoring components
- 95% coverage for battery prediction algorithms
- 90% coverage for firmware tracking mechanisms
- 95% coverage for calibration drift detection
- 90% coverage for gateway load balancing analytics

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful if it meets the following criteria:

1. Battery level forecasts are accurate within 3 days of actual depletion for 95% of devices
2. Firmware version inconsistencies are identified within 1 hour of occurrence
3. Sensor calibration drift is detected before readings deviate by more than 5% from actual values
4. Environmental condition correlations achieve at least 85% statistical confidence
5. Gateway load imbalances are identified when any gateway exceeds 25% above average load
6. The system scales effectively to monitor at least 10,000 devices simultaneously
7. Monitoring bandwidth consumption averages less than 1KB per device per hour
8. All components pass their respective test suites with required coverage levels

---

To set up your development environment:

1. Create a virtual environment:
   ```
   uv venv
   ```

2. Activate the virtual environment:
   ```
   source .venv/bin/activate
   ```

3. Install the required dependencies
   ```
   uv sync
   ```