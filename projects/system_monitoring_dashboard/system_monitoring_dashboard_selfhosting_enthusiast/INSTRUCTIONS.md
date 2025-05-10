# Home Server Monitoring System

## Overview
A comprehensive monitoring solution designed for home self-hosting environments that tracks energy consumption, hardware health, internet connectivity, and service accessibility. This system empowers enthusiasts to maintain reliable home services without depending on cloud infrastructure while providing accessible monitoring from any device.

## Persona Description
Sophia runs multiple services (media server, home automation, personal cloud) on hardware located in her home. She needs to monitor system performance and ensure reliability without complex infrastructure or cloud dependencies.

## Key Requirements

1. **Power Consumption Tracking**
   - Implement power usage monitoring that correlates system activities with energy consumption patterns
   - This is critical because home servers run 24/7, and understanding power usage helps optimize for energy efficiency and cost
   - Monitoring should identify which services and activities contribute most significantly to overall power consumption

2. **Mobile-Optimized Monitoring Interface API**
   - Design APIs that enable retrieving system status and alerts from any device regardless of location
   - This is essential because self-hosting enthusiasts need to check system health while away from home
   - The API must support low-bandwidth situations and provide concise status summaries

3. **Internet Connection Quality Monitoring**
   - Create robust internet connectivity monitoring that detects outages, measures performance, and logs connectivity issues
   - This is vital because reliable internet connectivity directly impacts the accessibility of self-hosted services
   - Monitoring should capture metrics like latency, jitter, packet loss, and bandwidth to provide a complete picture of connection quality

4. **Temperature and Hardware Health Metrics**
   - Develop hardware health monitoring capabilities for consumer-grade equipment without enterprise management features
   - This is important because home servers often use consumer hardware that lacks built-in monitoring capabilities
   - Monitoring should track system temperatures, disk health (S.M.A.R.T), fan speeds, and other hardware vitals

5. **Dynamic DNS Integration and External Accessibility**
   - Implement functionality to verify external accessibility of services and monitor dynamic DNS updates
   - This is crucial because self-hosted services must remain accessible from the internet despite residential IP changes
   - The system should confirm that port forwarding, DNS records, and public endpoints remain properly configured

## Technical Requirements

- **Testability Requirements**
  - All components must have unit tests with minimum 90% code coverage
  - Tests must use fixtures to simulate various hardware conditions and network states
  - Mocking should be used for hardware interfaces and external API dependencies
  - Integration tests must verify proper interaction with hardware monitoring interfaces
  - Parameterized tests must validate behavior across different system configurations

- **Performance Expectations**
  - Monitoring overhead must not impact the performance of hosted services
  - Power consumption monitoring must be accurate within ±5% when compared to physical power meters
  - Temperature monitoring must sample at least once per minute during normal operation
  - Network connectivity tests must detect outages within 30 seconds
  - Historical data must be efficiently stored to manage disk usage on limited hardware

- **Integration Points**
  - Direct hardware access for temperature and power metrics (via platform-specific APIs)
  - SMART disk monitoring interface
  - Network interface access for connectivity testing
  - Dynamic DNS service provider APIs
  - External service checking from both internal and external perspectives

- **Key Constraints**
  - Must function on consumer hardware without enterprise management features
  - Cannot depend on cloud services for core functionality
  - Must operate with minimal resource overhead on systems simultaneously running other services
  - Storage requirements must be configurable to accommodate limited disk space
  - Must work within a home network environment with typical NAT/firewall configurations

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide:

1. **Energy Usage Monitoring**
   - Direct power consumption measurement through compatible interfaces (ACPI, RAPL, etc.)
   - Correlation between system load, active services, and power consumption
   - Historical power usage tracking with time-based patterns and anomaly detection
   - Energy efficiency recommendations based on usage patterns
   - Cost calculations based on configurable electricity rates

2. **Mobile-First Status API**
   - RESTful API endpoints providing system status summaries
   - Authentication system supporting secure remote access
   - Bandwidth-efficient data structures for mobile consumption
   - Push notification capabilities for critical alerts
   - Query parameters for filtering data based on client needs

3. **Network Quality Analysis**
   - Continuous monitoring of internet connectivity and performance
   - Detailed logging of outages with duration and impact assessment
   - Speed testing on a configurable schedule
   - Latency tracking to key internet services and custom endpoints
   - Historical connectivity data for troubleshooting recurring issues

4. **Hardware Health Subsystem**
   - CPU, GPU, and system temperature monitoring
   - Fan speed monitoring and correlation with system load
   - S.M.A.R.T. disk health monitoring and predictive failure analysis
   - RAM and motherboard sensor data collection where available
   - Hardware performance degradation detection

5. **External Accessibility Verification**
   - Dynamic DNS update monitoring and verification
   - External service availability checking from internet perspective
   - Port forwarding and firewall configuration validation
   - SSL certificate expiration monitoring
   - Domain name resolution validation

## Testing Requirements

- **Key Functionalities to Verify**
  - Accuracy of power consumption measurements across different load levels
  - Responsiveness and data efficiency of the mobile status API
  - Reliability of internet connectivity monitoring and outage detection
  - Precision of temperature and hardware health monitoring
  - Effectiveness of external service accessibility verification

- **Critical User Scenarios**
  - Identifying power-hungry services consuming excessive electricity
  - Receiving immediate notification when internet connectivity is lost
  - Detecting potential hardware failures before they occur
  - Confirming services remain accessible after dynamic DNS updates
  - Monitoring system health while away from home

- **Performance Benchmarks**
  - Power monitoring accuracy within ±5% of physical measurement devices
  - API response time under 500ms even with 30 days of historical data
  - Internet outage detection within 30 seconds of occurrence
  - Temperature monitoring within ±2°C of actual component temperatures
  - External accessibility checks completed within 60 seconds

- **Edge Cases and Error Conditions**
  - System behavior when hardware monitoring interfaces return unexpected values
  - Recovery after extended power or network outages
  - Handling of sensor failures or unreliable hardware readings
  - Behavior during severe system resource constraints
  - Proper functioning when dynamic DNS services are unavailable

- **Test Coverage Requirements**
  - Minimum 90% code coverage for all components
  - 100% coverage for critical monitoring paths
  - All hardware interfaces must have comprehensive mocking tests
  - Network failure scenarios must be thoroughly tested
  - API security and authentication edge cases must be fully validated

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

A successful implementation will:

1. Measure power consumption with at least 95% accuracy compared to physical power meters
2. Provide system status through an API accessible from mobile devices with response times under 500ms
3. Detect and log internet outages with timestamps accurate to within 30 seconds
4. Monitor hardware temperatures within 2°C accuracy and predict disk failures at least 48 hours in advance
5. Verify external service accessibility and dynamic DNS status with 99% reliability
6. Store at least 90 days of historical data while using less than 1GB of storage
7. Operate with less than 3% CPU overhead and 100MB memory footprint on the host system
8. Achieve 90% test coverage across all modules

## Setup and Development

To set up your development environment:

1. Use `uv init --lib` to initialize the project structure and setup the virtual environment
2. Install dependencies with `uv sync`
3. Run the application with `uv run python your_script.py`
4. Run tests with `uv run pytest`
5. Format code with `uv run ruff format`