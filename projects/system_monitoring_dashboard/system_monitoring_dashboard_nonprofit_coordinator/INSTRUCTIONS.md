# Nonprofit-Friendly Monitoring System

## Overview
A simplified, accessible monitoring system designed for nonprofit organizations with limited technical resources that provides intuitive status indicators, suggests resolution steps for common issues, supports scheduled maintenance windows, implements role-based access controls for volunteers, and minimizes resource requirements for older donated hardware.

## Persona Description
Miguel supports IT systems for a nonprofit organization with limited budget and technical staff. He needs simple, reliable monitoring that can be understood by occasional volunteers who help maintain systems.

## Key Requirements

1. **Simplified Status Indicator System**
   - Implement a red/yellow/green status categorization that clearly communicates system health to non-technical stakeholders
   - This is critical because nonprofit staff with limited technical background need clear, actionable status information
   - The indicators must abstract complex technical metrics into simple health categories with clear explanations

2. **Guided Resolution Suggestions**
   - Create an automated recommendation system that suggests specific steps to resolve common system issues
   - This is essential because volunteers without extensive IT experience need guidance to address problems
   - The suggestions must be clear, step-by-step, and tailored to the skill level of occasional technical helpers

3. **Scheduled Maintenance Mode**
   - Develop maintenance window functionality that suppresses alerts during planned maintenance activities
   - This is vital because false alarms during scheduled maintenance discourage volunteer engagement
   - The scheduling must be simple to configure, with clear indicators when a system is in maintenance mode

4. **Volunteer Access Control System**
   - Implement role-based access controls that limit system management capabilities based on volunteer roles
   - This is important because nonprofits rely on various volunteers with different skill levels and trustworthiness
   - The access system must balance security with ease of use for non-technical administrators

5. **Minimal Resource Requirements**
   - Design a lightweight monitoring solution optimized for older donated hardware with limited capabilities
   - This is crucial because nonprofits often operate on limited budgets with donated technology
   - The system must function effectively on hardware that is 5-10 years old while still providing essential monitoring

## Technical Requirements

- **Testability Requirements**
  - All components must have unit tests with minimum 80% code coverage
  - Test fixtures for simulating various nonprofit hardware environments
  - Simplified test procedures that can be run by administrators with limited technical background
  - Parameterized tests for different volunteer access role combinations
  - Test cases for performance on resource-constrained systems

- **Performance Expectations**
  - Monitoring must function on systems with as little as 1GB RAM and single-core CPUs
  - Status calculations must complete within 30 seconds even on older hardware
  - Installation must require fewer than 10 steps to complete successfully
  - Storage requirements must not exceed 1GB for a small nonprofit environment
  - System must operate with less than 10% CPU impact on monitored services

- **Integration Points**
  - Common nonprofit applications (fundraising software, volunteer management, CRM)
  - Essential services (email, file sharing, website)
  - Simple authentication systems (local accounts, basic LDAP)
  - Email notification for alerts
  - Basic backup verification

- **Key Constraints**
  - Must operate without requiring dedicated monitoring hardware
  - Cannot depend on extensive technical knowledge for day-to-day operation
  - Documentation must be accessible to non-technical users
  - Installation and updates must be simple and reliable
  - Must function effectively with minimal configuration

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide:

1. **Simplified Health Monitoring**
   - Clear red/yellow/green status categorization for all monitored components
   - Plain-language explanations of status conditions
   - Simple thresholds for critical services that non-technical users can understand
   - Status summarization that highlights the most critical issues
   - Historical status tracking with easy-to-understand trends

2. **Problem Resolution Guidance**
   - Automated troubleshooting recommendations for common issues
   - Step-by-step resolution procedures tailored to volunteer skill levels
   - Knowledge base integration for recurring problems
   - Success tracking for recommended solutions
   - Escalation pathways when guided resolution fails

3. **Maintenance Management**
   - Simple scheduling interface for planned maintenance activities
   - Automatic suppression of alerts during maintenance windows
   - Notification of maintenance status to stakeholders
   - Verification of system recovery after maintenance completion
   - Historical record of maintenance activities and outcomes

4. **Volunteer Management System**
   - Definition of role-based access levels for different volunteer capabilities
   - Secure authentication with appropriate complexity for nonprofit environments
   - Audit logging of volunteer actions for accountability
   - Temporary access provisioning for one-time helpers
   - Self-service capabilities for basic monitoring functions

5. **Resource-Efficient Operation**
   - Optimized monitoring agent for older hardware
   - Configurable monitoring depth based on available resources
   - Graceful degradation when resources are constrained
   - Efficient storage utilization for historical data
   - Low-bandwidth operation for limited network environments

## Testing Requirements

- **Key Functionalities to Verify**
  - Accuracy of status indicators in representing actual system health
  - Effectiveness of resolution suggestions in addressing common problems
  - Reliability of maintenance mode in suppressing unnecessary alerts
  - Security of the volunteer access control system
  - Efficiency of the monitoring system on resource-constrained hardware

- **Critical User Scenarios**
  - Non-technical staff interpreting system status during a partial outage
  - Volunteer following guided resolution steps to solve a common issue
  - Coordinator scheduling maintenance and verifying alert suppression
  - Managing access for volunteers with varying technical capabilities
  - Deploying monitoring to an older donated server with limited resources

- **Performance Benchmarks**
  - Status updates must complete within 30 seconds on hardware with 1GB RAM
  - Resolution guidance must be provided within 60 seconds of issue detection
  - Maintenance mode changes must take effect within 5 minutes
  - Access control changes must apply within 2 minutes
  - System must use less than 200MB of RAM on monitoring server

- **Edge Cases and Error Conditions**
  - System behavior during extreme resource constraints
  - Recovery after unexpected monitoring service interruptions
  - Handling of conflicting maintenance schedules
  - Management of compromised volunteer credentials
  - Fallback modes when integration points are unavailable

- **Test Coverage Requirements**
  - Minimum 80% code coverage across all components
  - 100% coverage for volunteer access control modules
  - All status indicator algorithms must have dedicated test cases
  - Resource utilization paths must be thoroughly tested
  - Resolution suggestion logic must be verified for common scenarios

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

A successful implementation will:

1. Accurately represent system health with red/yellow/green indicators that non-technical staff can understand
2. Provide effective resolution guidance that enables volunteers to solve at least 80% of common issues
3. Properly suppress alerts during scheduled maintenance periods while maintaining monitoring visibility
4. Securely manage different access levels for at least 5 distinct volunteer roles
5. Function effectively on hardware with as little as 1GB RAM and single-core CPU
6. Complete installation with fewer than 10 steps on a standard system
7. Require less than 1GB of storage for 90 days of historical data
8. Maintain monitoring with less than 10% CPU overhead on monitored systems

## Setup and Development

To set up your development environment:

1. Use `uv init --lib` to initialize the project structure and setup the virtual environment
2. Install dependencies with `uv sync`
3. Run the application with `uv run python your_script.py`
4. Run tests with `uv run pytest`
5. Format code with `uv run ruff format`