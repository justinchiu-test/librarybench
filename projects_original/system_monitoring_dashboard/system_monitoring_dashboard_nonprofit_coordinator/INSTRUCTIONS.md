# Nonprofit Technology Monitoring Solution

A simplified monitoring system designed for nonprofit organizations with limited technical resources, focusing on ease of use, clear status indicators, and volunteer management.

## Overview

This implementation of PyMonitor is tailored for nonprofit organizations with limited technical staff, providing simplified status tracking, guided resolution steps, maintenance scheduling, volunteer access management, and minimal resource requirements to ensure critical systems remain operational with occasional volunteer assistance.

## Persona Description

Miguel supports IT systems for a nonprofit organization with limited budget and technical staff. He needs simple, reliable monitoring that can be understood by occasional volunteers who help maintain systems.

## Key Requirements

1. **Simplified Status Indicators**
   - Implement clear red/yellow/green status indicators for system health
   - Provide non-technical explanations of issues in plain language
   - Include severity classification for prioritization
   - Support categorization by service impact (e.g., "affects website" or "affects email")
   - Generate simplified summary reports for non-technical stakeholders
   - This is critical because nonprofit staff often lack technical expertise, and clear indicators help them understand when assistance is needed and which issues are most important.

2. **Automated Resolution Steps**
   - Provide documented, step-by-step resolution procedures for common issues
   - Include screenshots and simplified explanations with technical steps
   - Track resolution attempts and their outcomes
   - Support custom resolution guides for organization-specific systems
   - Include safety checks to prevent accidental system damage
   - This is critical because volunteers or non-technical staff may need to address issues when dedicated IT support is unavailable, and guided procedures reduce the risk of errors.

3. **Scheduled Maintenance Mode**
   - Implement maintenance windows to suppress alerts during planned work
   - Support recurring maintenance schedules for regular tasks
   - Include pre-maintenance checklists and post-maintenance verification
   - Provide maintenance activity logging for accountability
   - Automatically resume monitoring after scheduled maintenance period
   - This is critical because nonprofits often perform maintenance during off-hours to minimize disruption, and preventing false alerts during these periods reduces alert fatigue.

4. **Volunteer Access Controls**
   - Support role-based access for different volunteer skill levels
   - Implement audit logging of all volunteer actions
   - Allow temporary access grants with automatic expiration
   - Provide view-only roles for minimally trained volunteers
   - Include guided, limited-scope administrative functions for specific tasks
   - This is critical because nonprofits rely on volunteers with varying technical skills, and appropriate access controls ensure they can help without risking system integrity.

5. **Minimal Dependency Installation**
   - Design for operation on older, donated hardware with limited resources
   - Minimize external dependencies and software requirements
   - Support offline installation for environments with limited connectivity
   - Include fallback functionality when optimal resources are unavailable
   - Provide clear minimum requirements documentation
   - This is critical because nonprofit organizations often operate with donated, older hardware and cannot always update to the latest systems or install extensive dependencies.

## Technical Requirements

### Testability Requirements
- All monitoring components must be testable with minimal setup complexity
- Status indicators must be verifiable with predefined test scenarios
- Resolution steps must be testable for accuracy and completeness
- Maintenance mode functionality must be verifiable with simulated schedules
- Access control mechanisms must be testable for proper permission enforcement
- Resource usage must be measured and verified during testing

### Performance Expectations
- Run efficiently on hardware with minimum 1GHz CPU and 512MB RAM
- Support for monitoring at least 20 essential services
- Startup time under 30 seconds on reference hardware
- Alert generation within 1 minute of issue detection
- Storage requirements under 1GB for 6 months of history
- Minimal CPU usage during normal operation (less than 5%)

### Integration Points
- Basic email alerting via SMTP
- Simple file-based logging
- Common services monitoring (web, email, file sharing, database)
- Local authentication for volunteer management
- Basic scheduler for maintenance windows
- Standard system metrics collection (CPU, memory, disk, network)

### Key Constraints
- Must run on Windows 7/8/10 and common Linux distributions
- Cannot require administrative access for basic monitoring
- Must operate with SQLite or file-based storage (no external database requirement)
- Should function without cloud dependencies
- Cannot require specialized monitoring agents on all systems
- Must be installable by following simple, documented steps

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system should consist of these core modules:

1. **Simplified Monitoring Core**
   - Basic system metric collection (CPU, memory, disk, network)
   - Service availability checking via standard protocols
   - Status determination and classification
   - Non-technical explanation generation
   - Simplified reporting for stakeholders

2. **Resolution Guide Manager**
   - Procedure definition and storage
   - Step-by-step resolution presentation
   - Attempt tracking and outcome recording
   - Custom guide management
   - Validation of resolution effectiveness

3. **Maintenance Scheduler**
   - Maintenance window definition and management
   - Alert suppression during planned maintenance
   - Checklist generation and verification
   - Activity logging during maintenance
   - Automatic monitoring resumption

4. **Volunteer Access Controller**
   - Role definition and permission management
   - User authentication and authorization
   - Action auditing and logging
   - Temporary access management
   - Guided administrative functions

5. **Resource-Efficient Core**
   - Optimized metric collection
   - Configurable collection frequency
   - Storage management with automatic pruning
   - Offline operation capabilities
   - Graceful degradation on resource constraints

## Testing Requirements

### Key Functionalities to Verify
- Accurate representation of system status with clear indicators
- Effective presentation of resolution steps for common issues
- Reliable management of maintenance windows and alert suppression
- Proper enforcement of volunteer access controls
- Efficient operation on limited hardware resources

### Critical User Scenarios
- Non-technical staff identifying and understanding system issues
- Volunteers following guided resolution steps to fix problems
- Scheduling and managing maintenance windows
- Assigning appropriate access levels to different volunteers
- Operating on donated hardware with limited specifications

### Performance Benchmarks
- System startup under 30 seconds on reference hardware
- Alert generation within 1 minute of threshold violation
- Support for at least 20 monitored services simultaneously
- CPU usage below 5% during normal operation
- Memory footprint under 100MB during operation

### Edge Cases and Error Conditions
- Handling multiple simultaneous system issues
- Managing conflicting maintenance windows
- Recovering from incomplete resolution attempts
- Dealing with volunteers exceeding their authorized access
- Adapting to extremely resource-constrained environments

### Test Coverage Metrics
- Minimum 85% code coverage across all modules
- 100% coverage of status determination logic
- 100% coverage of resolution step presentation
- 90% coverage of maintenance scheduling
- 95% coverage of access control mechanisms
- 90% coverage of resource optimization code

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

1. **Intuitive Status Presentation**
   - Clear red/yellow/green indicators that accurately reflect system health
   - Non-technical explanations that effectively communicate issues
   - Appropriate categorization and prioritization of problems

2. **Effective Resolution Guidance**
   - Complete and accurate step-by-step procedures for common issues
   - Clear documentation that non-technical volunteers can follow
   - Tracking of resolution attempts and outcomes

3. **Reliable Maintenance Management**
   - Accurate suppression of alerts during scheduled maintenance
   - Proper resumption of monitoring after maintenance completion
   - Effective logging of maintenance activities

4. **Secure Volunteer Management**
   - Appropriate enforcement of role-based access controls
   - Reliable tracking of volunteer actions
   - Effective temporary access management

5. **Resource-Efficient Operation**
   - Demonstrated ability to run on limited hardware
   - Minimal dependency requirements
   - Appropriate resource usage under various conditions

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