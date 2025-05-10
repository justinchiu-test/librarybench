# IoT Device Fleet Monitoring System

## Overview
A specialized monitoring platform designed for industrial IoT deployments that tracks battery levels of wireless devices, monitors firmware versions across the device fleet, detects sensor calibration drift, correlates environmental conditions with device performance, and analyzes gateway connection load balancing to ensure reliable operation of distributed sensor networks.

## Persona Description
Amara oversees a network of IoT devices deployed across multiple industrial facilities. She needs to monitor both device health and the edge computing infrastructure supporting these devices.

## Key Requirements

1. **Battery Level Monitoring**
   - Implement comprehensive battery tracking for power-constrained wireless IoT devices
   - This is critical because battery failure is a primary cause of device outages in IoT deployments
   - The monitoring must predict battery depletion timeframes and prioritize maintenance based on criticality

2. **Firmware Version Management**
   - Create a firmware tracking system that monitors version consistency across the device fleet
   - This is essential because inconsistent firmware versions can cause reliability issues and security vulnerabilities
   - The tracking must identify outdated devices, verify successful updates, and manage deployment strategies

3. **Sensor Calibration Drift Detection**
   - Develop analytics capability to identify sensors exhibiting measurement drift requiring recalibration
   - This is vital because undetected calibration drift leads to inaccurate data and potentially unsafe conditions
   - The detection must analyze measurement patterns to identify statistical anomalies that indicate drift

4. **Environmental Condition Correlation**
   - Implement analysis that correlates environmental factors (temperature, humidity, vibration) with device performance
   - This is important because environmental conditions often impact IoT device reliability and measurement accuracy
   - The correlation must identify when conditions exceed operational parameters and affect device function

5. **Gateway Load Distribution Analysis**
   - Create monitoring for IoT gateway infrastructure to analyze the distribution of device connections
   - This is crucial because imbalanced gateway loading can cause connectivity issues and data transmission failures
   - The analysis must identify overloaded gateways, recommend load balancing actions, and detect communication bottlenecks

## Technical Requirements

- **Testability Requirements**
  - All components must have unit tests with minimum 85% code coverage
  - Mock IoT device communication for testing without physical devices
  - Test fixtures for various battery profiles, sensor types, and environmental conditions
  - Simulation framework for testing device failure scenarios
  - Parameterized tests for different device types, firmware versions, and gateway configurations

- **Performance Expectations**
  - Monitoring must handle data from at least 10,000 devices with 5-minute reporting intervals
  - Battery projection algorithms must predict depletion within ±10% accuracy
  - Calibration drift detection must identify significant drift within 24 hours
  - Environmental correlation analysis must process data with less than 5-minute delay
  - Gateway load analysis must update within 10 minutes of connection pattern changes

- **Integration Points**
  - IoT device communication protocols (MQTT, CoAP, etc.)
  - Time series databases for sensor data storage
  - Firmware management and update systems
  - Gateway management interfaces
  - Environmental monitoring systems

- **Key Constraints**
  - Must minimize additional network traffic to preserve battery life
  - Cannot depend on continuous connectivity for core monitoring functions
  - Must handle heterogeneous device types with different capabilities
  - Storage and processing must scale to accommodate thousands of devices
  - Analysis overhead must not impact gateway performance

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide:

1. **Power Management Intelligence**
   - Battery level tracking and historical discharge patterns
   - Predictive algorithms for estimating remaining battery life
   - Anomalous power consumption detection
   - Prioritization algorithms for maintenance scheduling
   - Correlation between device activity and power consumption

2. **Firmware Oversight System**
   - Inventory management of device firmware versions
   - Update verification and success/failure tracking
   - Version consistency analysis across device groups
   - Security vulnerability identification in outdated firmware
   - Update impact analysis on device performance

3. **Measurement Quality Analysis**
   - Statistical methods for detecting sensor drift
   - Comparison against known-good reference devices
   - Historical measurement trend analysis
   - Confidence scoring for sensor readings
   - Recalibration effectiveness verification

4. **Environmental Impact Assessment**
   - Collection and correlation of environmental telemetry
   - Device performance mapping to environmental conditions
   - Threshold monitoring for operational parameters
   - Predictive analytics for environmental-related failures
   - Seasonal pattern identification and preparation

5. **Gateway Performance Optimization**
   - Connection distribution monitoring across gateway infrastructure
   - Load balancing recommendation engine
   - Communication failure pattern analysis
   - Throughput and latency measurement
   - Gateway resource utilization tracking

## Testing Requirements

- **Key Functionalities to Verify**
  - Accuracy of battery life predictions across different device types
  - Completeness of firmware version tracking and update verification
  - Effectiveness of calibration drift detection algorithms
  - Reliability of environmental condition correlation with device performance
  - Precision of gateway load distribution analysis

- **Critical User Scenarios**
  - Planning a battery replacement schedule based on depletion forecasts
  - Coordinating firmware updates across a heterogeneous device fleet
  - Identifying sensors requiring recalibration before measurement quality degrades
  - Responding to environmental conditions that threaten device operation
  - Rebalancing connections across gateways to prevent communication bottlenecks

- **Performance Benchmarks**
  - System must process status updates from 10,000 devices every 5 minutes
  - Battery projections must achieve 90% accuracy for predictions up to 30 days out
  - Calibration drift detection must identify 95% of significant drift cases with fewer than 5% false positives
  - Environmental correlation must process at least 1,000 condition reports per minute
  - Gateway analysis must handle connection data from at least 100 gateways simultaneously

- **Edge Cases and Error Conditions**
  - System behavior during massive device reconnection events
  - Recovery after gateway or network outages
  - Handling of conflicting or erroneous sensor readings
  - Management of devices with faulty battery monitoring
  - Operation during partial infrastructure failures

- **Test Coverage Requirements**
  - Minimum 85% code coverage across all components
  - 100% coverage for battery prediction and calibration drift algorithms
  - All device communication protocols must have dedicated test cases
  - Error handling paths must be thoroughly tested
  - Scaling behavior must be verified through load testing

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

A successful implementation will:

1. Predict battery depletion timeframes with at least 90% accuracy up to 30 days in advance
2. Track firmware versions across 100% of connected devices and verify update completion
3. Detect sensor calibration drift with at least 95% accuracy and fewer than 5% false positives
4. Identify correlations between environmental conditions and device performance with statistical significance
5. Analyze gateway load distribution and suggest rebalancing when connection differences exceed 30%
6. Scale to handle at least 10,000 devices with 5-minute reporting intervals
7. Maintain data for at least 90 days for trend analysis
8. Achieve 85% test coverage across all monitoring modules

## Setup and Development

To set up your development environment:

1. Use `uv init --lib` to initialize the project structure and setup the virtual environment
2. Install dependencies with `uv sync`
3. Run the application with `uv run python your_script.py`
4. Run tests with `uv run pytest`
5. Format code with `uv run ruff format`