# Home Infrastructure Monitoring System

A comprehensive monitoring solution for self-hosted services that operates independently without cloud dependencies, optimized for home environments.

## Overview

The Home Infrastructure Monitoring System is a specialized implementation of the PyMonitor system designed for self-hosting enthusiasts who run multiple services on personal hardware. It emphasizes energy efficiency tracking, hardware health monitoring, and remote accessibility while maintaining complete independence from third-party services or cloud infrastructure.

## Persona Description

Sophia runs multiple services (media server, home automation, personal cloud) on hardware located in her home. She needs to monitor system performance and ensure reliability without complex infrastructure or cloud dependencies.

## Key Requirements

1. **Power Consumption Tracking** - Implement functionality to monitor and correlate system activity with energy usage. This is critical for Sophia as it helps her maintain energy-efficient operations, optimize server scheduling, and understand the cost implications of running her self-hosted infrastructure.

2. **Mobile-Friendly Access** - Create an API-based system that allows checking system status from anywhere via mobile devices. Sophia needs this because she wants to monitor her home systems while away, ensuring she can respond to critical issues regardless of her location.

3. **Internet Connection Quality Monitoring** - Develop capabilities to detect, log, and analyze internet connection quality, including outages. This is essential for Sophia as her self-hosted services depend on reliable internet connectivity, and she needs to diagnose connectivity issues affecting external access to her services.

4. **Temperature and Hardware Health Monitoring** - Implement detailed temperature tracking and hardware health metrics for consumer-grade equipment without built-in management features. This requirement is important because Sophia's home hardware lacks enterprise monitoring capabilities but still needs protection from thermal issues and hardware failures.

5. **Dynamic DNS Integration** - Create functionality to track the external accessibility of self-hosted services, particularly with changing IP addresses. Sophia requires this to ensure her services remain accessible from outside her network, detecting when DNS updates fail or when services become unreachable.

## Technical Requirements

### Testability Requirements
- All monitoring components must be testable with pytest
- Hardware metrics collection must support mocking for testing without physical sensors
- Network monitoring must include simulation capabilities for testing without actual connection issues
- Power consumption correlation algorithms must be verifiable with predefined data sets

### Performance Expectations
- Monitoring system must use minimal resources (less than 5% CPU, 200MB RAM)
- Data collection should be configurable from 10-second to 15-minute intervals
- Database must efficiently store at least 12 months of data for trend analysis
- API responses should be delivered in under 500ms even on low-power hardware

### Integration Points
- SNMP for compatible network devices
- SMART data for disk health monitoring
- Standardized power monitoring APIs or devices (where available)
- Dynamic DNS providers' APIs
- Temperature sensors (software and hardware-based where available)

### Key Constraints
- Must function without cloud dependencies or internet access
- Must operate on consumer hardware (including Raspberry Pi, NAS devices, etc.)
- Cannot rely on specialized enterprise monitoring hardware
- Must work with dynamic IP addresses and residential internet connections
- Must support secure remote access without requiring VPN configuration

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Home Infrastructure Monitoring System must implement the following core functionality:

1. **Energy Efficiency Monitoring**
   - Power consumption tracking via compatible smart plugs or built-in sensors
   - Correlation between system workload and energy consumption
   - Idle vs. active power usage analysis
   - Power efficiency recommendations based on usage patterns
   - Long-term cost estimation based on energy pricing

2. **Remote Monitoring Capabilities**
   - RESTful API for remote service monitoring
   - Secure access with token-based authentication
   - Essential metrics accessible via lightweight API calls
   - Status summary endpoints optimized for mobile consumption
   - Push notification mechanism for critical alerts

3. **Network Quality Analysis**
   - Internet connection uptime monitoring
   - Bandwidth utilization tracking
   - Latency and packet loss measurement
   - ISP performance trend analysis
   - Outage detection and logging with timestamps

4. **Hardware Health Management**
   - Temperature monitoring for CPUs, drives, and enclosures
   - Fan speed tracking where applicable
   - SMART attribute monitoring for storage devices
   - Early warning system for hardware issues
   - Historical trend analysis for wear prediction

5. **External Access Verification**
   - Dynamic DNS update verification
   - External service accessibility checking
   - Port availability monitoring
   - SSL certificate expiration tracking
   - Service response time measurement from outside the network

## Testing Requirements

The implementation must include comprehensive tests that validate:

### Key Functionalities Verification
- Accuracy of power consumption measurements and correlation
- Reliability of hardware temperature and health data collection
- Precision of network quality metrics under various conditions
- Effectiveness of dynamic DNS monitoring and verification
- Security of the remote access API implementation

### Critical User Scenarios
- Detecting and alerting on hardware overheating conditions
- Identifying power consumption anomalies during different usage patterns
- Receiving alerts during internet connection outages or degradation
- Monitoring multiple services running on the same physical hardware
- Accessing critical system information remotely during potential issues

### Performance Benchmarks
- Resource utilization of the monitoring system itself
- Storage efficiency for long-term metric retention
- API response times under various system loads
- Alert notification delivery times for critical issues
- Data collection impact on monitored system performance

### Edge Cases and Error Handling
- Behavior during complete internet outages
- Handling of hardware sensor failures or incorrect readings
- Recovery after monitoring system restarts or crashes
- Operation during dynamic IP address changes
- Data integrity during power interruptions

### Required Test Coverage
- 90% code coverage for core monitoring functionality
- 100% coverage for alert and notification logic
- 95% coverage for network monitoring components
- 95% coverage for hardware health monitoring
- 90% coverage for power correlation algorithms

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful if it meets the following criteria:

1. Power consumption correlation is accurate within 10% of actual measurements
2. Hardware temperature monitoring provides early warning at least 10 minutes before critical thresholds
3. Internet outages are detected within 30 seconds and logged with correct timestamps
4. System is accessible remotely within 5 seconds of requesting data, even on mobile connections
5. External service accessibility is verified at least every 5 minutes with correct status reporting
6. All data is retained for at least 12 months for long-term trend analysis
7. System operates reliably on low-power devices like Raspberry Pi
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