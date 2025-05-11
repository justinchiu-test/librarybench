# Home Infrastructure Monitoring System

A comprehensive monitoring solution designed specifically for self-hosted home services, with a focus on power usage, hardware health, and service accessibility.

## Overview

This implementation of PyMonitor is tailored for home lab environments where individuals run multiple services (media servers, home automation, personal cloud storage) on their own hardware. It emphasizes energy efficiency, remote accessibility, and hardware health monitoring without requiring enterprise-grade equipment or complex infrastructure.

## Persona Description

Sophia runs multiple services (media server, home automation, personal cloud) on hardware located in her home. She needs to monitor system performance and ensure reliability without complex infrastructure or cloud dependencies.

## Key Requirements

1. **Power Consumption Tracking**
   - Monitor power usage across systems using compatible power meters or estimation algorithms
   - Correlate system activity (CPU/GPU/disk) with energy consumption
   - Generate reports on energy efficiency and cost impacts
   - Identify power-hungry processes and optimization opportunities
   - Track long-term trends in power usage by service and system
   - This is critical because self-hosting enthusiasts are often concerned about the ongoing electricity costs of running home servers 24/7.

2. **Mobile-Friendly Interface**
   - Provide REST API endpoints optimized for mobile consumption
   - Support secure remote access to monitoring data from outside the home network
   - Implement bandwidth-efficient data summaries for mobile viewing
   - Enable alert acknowledgment and basic control functions remotely
   - Support push notifications for critical system events
   - This is critical because home lab operators need visibility into their systems while away from home to address issues before they become critical.

3. **Internet Connection Quality Monitoring**
   - Track latency, packet loss, and bandwidth to key internet destinations
   - Detect and log internet outages with precise timing
   - Monitor DNS resolution performance and failures
   - Test accessibility of self-hosted services from external perspectives
   - Correlate connection issues with ISP performance
   - This is critical because internet reliability directly impacts the accessibility of self-hosted services from outside the home.

4. **Temperature and Hardware Health Metrics**
   - Monitor CPU, GPU, disk temperatures and fan speeds
   - Track S.M.A.R.T. data for storage devices
   - Monitor UPS status and runtime estimates
   - Detect and alert on hardware anomalies before failure
   - Support consumer-grade hardware without enterprise management features
   - This is critical because consumer hardware used in home labs often lacks enterprise management capabilities and can be prone to thermal issues when run continuously.

5. **Dynamic DNS Integration**
   - Monitor and verify dynamic DNS updates
   - Track record changes and update history
   - Test external accessibility through DNS names
   - Alert on DNS resolution failures or inconsistencies
   - Support common Dynamic DNS providers (DuckDNS, No-IP, etc.)
   - This is critical because self-hosting enthusiasts rely on dynamic DNS services to make their home services accessible from the internet despite changing IP addresses.

## Technical Requirements

### Testability Requirements
- All monitoring components must be testable with pytest
- Hardware sensor monitoring must support simulated inputs for testing
- Network tests must be mockable to simulate various connectivity scenarios
- Power monitoring algorithms must be verifiable with test fixtures
- API endpoints must be fully testable without requiring actual mobile devices

### Performance Expectations
- Minimal impact on monitored systems (less than 3% CPU, 100MB RAM)
- Support for monitoring at least 10 services on modest hardware (Raspberry Pi-level)
- Data retention of at least 12 months with efficient storage (under 5GB)
- API response times under 300ms even on resource-constrained systems
- Bandwidth usage for remote monitoring under 5MB per day

### Integration Points
- Power meters and UPS monitoring (via USB, network, or estimation)
- Hardware sensors (via standard libraries like lm-sensors, py-sensors)
- Dynamic DNS providers (via APIs)
- Internet quality testing (via configurable external endpoints)
- Network diagnostics (ping, traceroute, DNS resolution)

### Key Constraints
- Must operate on consumer hardware including ARM devices (Raspberry Pi)
- Cannot rely on enterprise management protocols not available on consumer hardware
- Must function without cloud dependencies
- Should minimize external dependencies to reduce security exposure
- Must operate efficiently on low-power devices
- Storage must use efficient formats to work within home storage constraints

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system should consist of these core modules:

1. **Power Monitoring Module**
   - Direct integration with supported UPS and power monitoring devices
   - Power estimation based on component utilization when direct measurement is unavailable
   - Historical trend analysis for power consumption
   - Cost calculation based on configurable electricity rates
   - Correlation engine to link system activities with power usage

2. **System Health Monitor**
   - Temperature monitoring for CPU, GPU, and system ambient sensors
   - S.M.A.R.T. data collection and analysis
   - Fan speed monitoring and control (where supported)
   - Hardware performance metrics (CPU frequency, throttling events)
   - Predictive failure analysis based on hardware metrics

3. **Internet Quality Monitor**
   - Connection quality testing to configurable endpoints
   - Outage detection and duration tracking
   - Bandwidth monitoring and trend analysis
   - DNS resolution testing and performance metrics
   - External service accessibility verification

4. **Dynamic DNS Manager**
   - Integration with popular DDNS providers
   - Update verification and failure handling
   - Historical tracking of IP changes
   - External resolution testing from configurable checkpoints
   - Alerting on resolution failures or inconsistencies

5. **API and Notification System**
   - RESTful API with optimized endpoints for mobile consumption
   - Authentication and secure remote access
   - Push notification integration for mobile alerts
   - Bandwidth-efficient data summaries and visualizations
   - Remote control capabilities for basic system functions

## Testing Requirements

### Key Functionalities to Verify
- Accurate power consumption monitoring and correlation with system activity
- Reliable temperature and hardware health monitoring
- Precise internet connection quality metrics and outage detection
- Effective dynamic DNS monitoring and verification
- Secure and efficient remote access to monitoring data

### Critical User Scenarios
- Monitoring power consumption trends over time
- Receiving alerts about hardware issues before failure occurs
- Tracking and responding to internet outages
- Verifying external accessibility of self-hosted services
- Remotely checking system status while away from home

### Performance Benchmarks
- Power monitoring accuracy within 10% of actual measurements
- Temperature monitoring within 2°C of actual readings
- Internet quality metrics with 95% accuracy compared to reference tools
- API response times under 300ms on reference hardware
- Data storage efficiency maintaining 12 months of history in under 5GB

### Edge Cases and Error Conditions
- Handling sensor failures or unavailable hardware metrics
- Graceful operation during internet outages
- Recovery after power failures without data loss
- Managing conflicting data from multiple measurement sources
- Adapting to system sleep states and power management

### Test Coverage Metrics
- Minimum 90% code coverage for all modules
- 100% coverage of hardware health monitoring logic
- 100% coverage of power estimation algorithms
- 100% coverage of internet quality testing
- 95% coverage of dynamic DNS integration
- 90% coverage of API endpoints

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

1. **Effective Power Monitoring**
   - Demonstrated ability to track and correlate power usage with system activity
   - Generation of accurate power consumption reports and trends
   - Identification of power-intensive processes and services

2. **Accessible Remote Monitoring**
   - Secure access to system data from outside the home network
   - Efficient mobile-optimized API endpoints
   - Functional remote notification and control capabilities

3. **Comprehensive Internet Quality Tracking**
   - Accurate detection and logging of internet outages
   - Reliable measurement of connection quality metrics
   - Correlation of internet issues with service accessibility

4. **Detailed Hardware Health Monitoring**
   - Accurate temperature and fan speed monitoring
   - Effective S.M.A.R.T. data analysis for early warning
   - Reliable detection of hardware anomalies

5. **Robust Dynamic DNS Management**
   - Verified integration with common DDNS providers
   - Accurate tracking of DNS updates and accessibility
   - Reliable alerting on DNS resolution issues

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