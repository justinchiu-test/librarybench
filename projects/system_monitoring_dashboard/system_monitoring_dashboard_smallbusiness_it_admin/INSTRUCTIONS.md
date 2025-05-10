# Small Business System Monitoring Solution

## Overview
A lightweight, resource-efficient monitoring system tailored for small business environments that enables a single IT administrator to effectively monitor critical servers and business applications without requiring enterprise-grade infrastructure or budget. This system provides focused alerts during business hours, generates management-friendly reports, and ensures critical business services remain operational.

## Persona Description
Marcus manages IT infrastructure for a growing e-commerce business with limited technical resources. He needs to monitor critical servers and services without dedicating an entire system or significant budget to enterprise-grade monitoring solutions.

## Key Requirements

1. **Low-Footprint Monitoring Agent**
   - Implement a monitoring agent with minimal CPU, memory, and disk usage (less than 5% of system resources)
   - This is critical because production systems must maintain optimal performance for business operations while being monitored
   - The agent must work efficiently on modest server hardware common in small business environments

2. **Business Hours Alert Profiles**
   - Create configurable alert thresholds with different sensitivity levels for business hours versus off-hours
   - This is vital because issues during business hours require immediate attention to prevent revenue loss, while off-hours alerts can be less aggressive
   - Support for different notification urgency based on time of day and business calendar

3. **Management-Friendly Summary Reports**
   - Generate automatically scheduled reports with clear visualizations and non-technical language
   - This is essential for justifying IT investments to business stakeholders who lack technical background
   - Reports must highlight business impact metrics rather than pure technical measurements

4. **Business Service Availability Monitoring**
   - Monitor critical business applications and payment processing systems beyond basic infrastructure metrics
   - This is crucial because service availability directly impacts revenue generation and customer satisfaction
   - Include application-layer checks for key business functions (shopping cart, payment processing, etc.)

5. **Streamlined Deployment Process**
   - Provide a simplified installation and configuration process designed for a single administrator without specialized expertise
   - This is important because small businesses lack dedicated monitoring specialists for complex deployments
   - Include sensible defaults and guided setup for common small business server configurations

## Technical Requirements

- **Testability Requirements**
  - All monitoring components must have comprehensive unit tests with at least 85% code coverage
  - Mock objects must be used for simulating various system conditions and alert scenarios
  - Tests must verify behavior across different operating systems commonly used in small business environments
  - Performance tests must confirm the monitoring agent maintains low resource utilization

- **Performance Expectations**
  - Monitoring agent must use less than 5% CPU and 100MB RAM on target systems
  - Data collection intervals must be configurable with a minimum resolution of 10 seconds
  - Storage efficiency must allow at least 30 days of historical data within 500MB of disk space
  - Alert processing and notification dispatch must occur within 15 seconds of threshold violation

- **Integration Points**
  - Email integration for sending alerts and reports (SMTP support required)
  - HTTP/HTTPS service checking for web application monitoring
  - Database connectivity checks for common database systems (MySQL, PostgreSQL)
  - Standard protocol support (ICMP, TCP, HTTP) for basic connectivity testing
  - Filesystem access for log analysis and storage monitoring

- **Key Constraints**
  - Must operate without requiring administrative/root privileges where possible
  - Cannot depend on cloud services for core functionality
  - Must function on common small business operating systems (Windows Server, Linux)
  - Cannot require additional infrastructure components beyond the monitoring system itself
  - Storage and retrieval mechanisms must be simple and reliable (e.g., SQLite, file-based storage)

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide:

1. **Resource-Efficient Data Collection**
   - CPU, memory, disk, and network usage collection with minimal system impact
   - Process-level monitoring for identifying resource-intensive applications
   - Service status checking for critical business applications
   - Event log and system log monitoring for error conditions
   - Collection frequency that balances timeliness with performance impact

2. **Intelligent Alert Management**
   - Time-aware thresholds that adjust based on business hours configuration
   - Alert deduplication to prevent notification storms during major issues
   - Escalation pathways for alerts that remain unacknowledged
   - Alert categorization by business impact and urgency
   - Rate limiting to prevent overwhelming a single administrator

3. **Business-Oriented Reporting**
   - Automated report generation on daily, weekly, and monthly schedules
   - Executive summaries highlighting key performance metrics in business terms
   - Availability calculations relevant to business operations (e.g., "99.9% uptime during business hours")
   - Problem summaries with resolution times and business impact estimates
   - Capacity planning projections based on historical growth patterns

4. **Service-Level Monitoring**
   - End-to-end transaction testing for critical business flows
   - API response time measurement for internal and external services
   - Database query performance monitoring
   - Payment gateway availability and response time tracking
   - Customer-facing website performance and availability metrics

5. **Simplified Deployment and Management**
   - Automated discovery of common services and monitoring targets
   - Template-based configuration for typical small business services
   - Self-testing capabilities to verify monitoring system health
   - Automatic updates for monitoring rules and checks
   - Configuration backup and restoration capabilities

## Testing Requirements

- **Key Functionalities to Verify**
  - Accuracy of system metric collection under various load conditions
  - Correct functioning of time-based alert profiles (business hours vs. off-hours)
  - Proper generation and formatting of management reports
  - Reliable detection of business service availability issues
  - Successful completion of the deployment and configuration process

- **Critical User Scenarios**
  - Setting up monitoring on a new server with minimal configuration
  - Receiving and responding to alerts during business hours
  - Generating and interpreting executive reports
  - Detecting and diagnosing a failing business service
  - Adjusting monitoring parameters as business needs change

- **Performance Benchmarks**
  - Agent CPU usage must remain below 5% even during intensive data collection
  - Alert notification time must be under 15 seconds from threshold violation
  - Report generation must complete within 60 seconds for 30 days of historical data
  - System must support monitoring at least 20 business services simultaneously
  - Historical data queries must return results within 5 seconds

- **Edge Cases and Error Conditions**
  - System behavior during network partitioning between monitoring components
  - Proper functioning during target system resource exhaustion
  - Recovery after unexpected monitoring agent termination
  - Handling of corrupt or incomplete historical data
  - Behavior when business service checks timeout or return ambiguous results

- **Test Coverage Requirements**
  - Minimum 85% code coverage for overall test suite
  - 100% coverage for alert notification and business service checking modules
  - All public APIs must have interface tests
  - All configuration parameters must have validation tests
  - System behavior must be tested across supported operating systems

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

A successful implementation will:

1. Maintain a monitoring agent resource footprint below 5% CPU and 100MB RAM during normal operation
2. Successfully detect and alert on at least 95% of simulated business service failures within 30 seconds
3. Generate executive reports that accurately reflect system status using business-friendly terminology and visualizations
4. Provide different alert sensitivity and notification behavior during and outside configured business hours
5. Enable a single administrator to deploy the complete monitoring solution in under 30 minutes
6. Store and analyze at least 30 days of historical performance data while staying within a 500MB storage footprint
7. Support monitoring of at least 5 servers and 20 business services simultaneously from a single monitoring instance
8. Achieve at least 85% test coverage across all modules with 100% for critical alert pathways

## Setup and Development

To set up your development environment:

1. Use `uv init --lib` to initialize the project structure and setup the virtual environment
2. Install dependencies with `uv sync`
3. Run the application with `uv run python your_script.py`
4. Run tests with `uv run pytest`
5. Format code with `uv run ruff format`