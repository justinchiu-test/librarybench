# Small Business Monitoring Solution

A lightweight system monitoring solution tailored for small business IT administrators needing to track critical servers and services without enterprise-grade resources.

## Overview

This implementation of PyMonitor focuses on creating a resource-efficient, easy-to-deploy monitoring system that requires minimal technical expertise to set up and maintain. It prioritizes simple alerting, non-technical reporting for management, and service monitoring without imposing significant overhead on production systems.

## Persona Description

Marcus manages IT infrastructure for a growing e-commerce business with limited technical resources. He needs to monitor critical servers and services without dedicating an entire system or significant budget to enterprise-grade monitoring solutions.

## Key Requirements

1. **Small Footprint Agent**
   - Implement a monitoring agent with minimal CPU and memory utilization (less than 2% CPU and 50MB RAM)
   - Enable throttling capabilities to reduce resource impact during high system load
   - Allow for customizable collection intervals to balance monitoring detail with system impact
   - Support for silent installation and background operation with minimal dependencies
   - This is critical because production systems in small businesses often cannot afford dedicated monitoring resources.

2. **Business Hours Alerting Profiles**
   - Create configurable alerting schedules with different thresholds for work hours vs. off-hours
   - Support emergency vs. non-emergency classification of alerts based on time of day
   - Allow definition of business holidays and special operating hours
   - Provide escalation paths that differ based on business hours
   - This is critical because small businesses have limited IT staff who need to prioritize work-hour issues and only be disturbed after-hours for emergencies.

3. **Non-Technical Summary Reports**
   - Generate executive-friendly system health reports using clear language and visual indicators
   - Include uptime statistics and reliability metrics in business terms (e.g., "99.9% availability")
   - Provide cost-impact estimates for system issues when possible
   - Support scheduled delivery of reports to management
   - This is critical because IT administrators in small businesses must regularly justify expenses and communicate system status to non-technical management.

4. **Service Availability Checks**
   - Monitor critical business applications (web servers, databases, payment processing)
   - Track external service dependencies like payment gateways or shipping APIs
   - Measure application responsiveness from an end-user perspective
   - Detect service failures with specific error indicators, not just binary up/down status
   - This is critical because small businesses rely heavily on a few key applications and services that directly impact revenue generation.

5. **Single-Admin Deployment**
   - Design a straightforward setup process with minimal configuration requirements
   - Provide sensible defaults appropriate for small business environments
   - Include clear documentation with step-by-step instructions
   - Limit technical jargon and assumptions about specialized knowledge
   - This is critical because small businesses often have a single IT person responsible for all systems who cannot afford extensive training or complex deployment processes.

## Technical Requirements

### Testability Requirements
- All components must be testable in isolation using pytest
- Mock external dependencies (servers, services, email) for testing
- Include test fixtures that simulate various system load scenarios
- Support parametrized tests for different alert thresholds and scheduling scenarios
- Allow for simulated time progression for testing time-based features

### Performance Expectations
- Monitoring agent must use less than 2% CPU and 50MB RAM on monitored systems
- Report generation must complete in under 30 seconds
- Alert triggers must fire within 15 seconds of threshold violation
- Database storage requirements should not exceed 1GB for 1 month of history
- API endpoints must respond in under 500ms

### Integration Points
- Email server integration for alerts and reports
- HTTP/HTTPS service checks for web applications
- Database connectivity checks for data services
- ICMP/ping for basic network availability
- REST API endpoints for service health checks

### Key Constraints
- Must run on Windows, Linux, and macOS servers
- Cannot require administrator/root privileges for basic monitoring
- Must operate without cloud dependencies
- Cannot rely on specialized hardware
- Should not require additional software installations beyond Python and minimal dependencies
- Database must be a simple file-based solution (SQLite)

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system should consist of these core modules:

1. **Lightweight Agent Module**
   - Self-throttling system metric collection (CPU, memory, disk, network)
   - Service availability monitoring through protocol-appropriate checks
   - Local storage of metrics with data retention policies
   - Self-updating capabilities from a central repository

2. **Alert Management Module**
   - Time-aware alerting with business hours configuration
   - Multiple notification methods (email, SMS, log)
   - Alert suppression for maintenance windows
   - Threshold configuration with different severity levels

3. **Reporting Module**
   - Regular system health summaries for technical and non-technical audiences
   - Uptime and reliability statistics
   - Performance trend analysis
   - Exportable formats (PDF, email-friendly HTML)

4. **Deployment Helper**
   - Configuration wizard with reasonable defaults
   - System requirements verification
   - Service installation utilities
   - Update mechanism

5. **API Layer**
   - RESTful endpoints for accessing monitoring data
   - Authentication and authorization
   - Query interface for historical metrics
   - Webhook support for integration with other systems

## Testing Requirements

### Key Functionalities to Verify
- Agent correctly collects system metrics with minimal resource impact
- Business hours alerting respects configured schedules and thresholds
- Reports accurately summarize system status in non-technical language
- Service checks correctly identify availability issues
- Single-admin deployment process functions as expected

### Critical User Scenarios
- Setting up monitoring on a new server with minimal configuration
- Receiving appropriate alerts during and outside business hours
- Generating and distributing executive reports
- Detecting and responding to service outages
- Adjusting thresholds to reduce alert noise

### Performance Benchmarks
- Agent impact must stay below 2% CPU and 50MB RAM
- Alert delivery must occur within 15 seconds of threshold violation
- Report generation must complete in under 30 seconds
- System must support monitoring at least 25 services
- Database should handle 30 days of metrics without exceeding 1GB

### Edge Cases and Error Conditions
- Handling network outages between monitoring components
- Properly managing disk space when storage is limited
- Graceful degradation when resources are constrained
- Recovering from incomplete or corrupted configurations
- Managing alert storms during widespread outages

### Test Coverage Metrics
- Minimum 85% code coverage for core functionality
- 100% coverage of alert logic and scheduling
- 100% coverage of report generation
- 100% coverage of deployment helpers
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

1. **Minimal Resource Utilization**
   - Demonstrable resource usage under 2% CPU and 50MB RAM on target systems
   - Validation through performance tests

2. **Effective Business Hours Alerting**
   - Properly categorized alerts based on business hours configuration
   - Correct threshold application based on time of day

3. **Management-Ready Reporting**
   - Reports that effectively communicate system health to non-technical stakeholders
   - Validated through test fixtures with predefined metrics and expected outputs

4. **Comprehensive Service Monitoring**
   - Accurate detection of service availability issues
   - Appropriate detail in service status reporting

5. **Simplified Deployment Process**
   - Complete setup with minimal steps
   - Default configurations appropriate for small business environments

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