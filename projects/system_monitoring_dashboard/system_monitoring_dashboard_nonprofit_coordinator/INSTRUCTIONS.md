# Simplified Nonprofit Systems Monitor

A streamlined, volunteer-friendly monitoring solution designed for nonprofit organizations with limited technical resources and diverse IT infrastructure.

## Overview

The Simplified Nonprofit Systems Monitor is a specialized implementation of the PyMonitor system tailored for nonprofit organizations with limited IT budgets and technical staff. It emphasizes simplicity, accessibility for non-technical stakeholders, guided issue resolution, maintenance planning, and compatibility with older donated hardware to create a monitoring solution that can be effectively managed by small teams and occasional volunteers.

## Persona Description

Miguel supports IT systems for a nonprofit organization with limited budget and technical staff. He needs simple, reliable monitoring that can be understood by occasional volunteers who help maintain systems.

## Key Requirements

1. **Simplified Status Indicators** - Implement an intuitive red/yellow/green status indication system for non-technical stakeholders. This is critical for Miguel because many decision-makers in the organization lack technical expertise, and simplified indicators enable them to quickly understand system health without requiring detailed technical knowledge.

2. **Guided Resolution Steps** - Develop an automated system that suggests documented remediation steps for common issues. Miguel needs this feature because he relies on volunteers with varying levels of technical skill to help maintain systems, and having clear, step-by-step resolution guidance ensures that problems can be addressed even when Miguel is unavailable.

3. **Scheduled Maintenance Mode** - Create functionality to temporarily suspend alerts during planned maintenance periods. This capability is essential for Miguel because it prevents alert fatigue during routine maintenance tasks and ensures that real issues don't get lost in the noise of expected alerts from planned work.

4. **Volunteer Access Controls** - Implement role-based monitoring access with granular permissions for volunteer staff. This is important for Miguel as it allows him to safely delegate monitoring responsibilities to volunteers based on their skill level, while limiting access to sensitive systems or critical infrastructure.

5. **Minimal Dependency Installation** - Design a lightweight monitoring system compatible with older donated hardware. Miguel requires this because nonprofits often operate with donated, older equipment, and the monitoring system must function effectively on these limited resources without requiring hardware upgrades.

## Technical Requirements

### Testability Requirements
- All monitoring components must be testable with pytest
- Status determination logic must be verifiable with predefined conditions
- Resolution recommendation system must be testable with common issue scenarios
- Maintenance mode functionality must be validated for alert suppression accuracy
- Access control mechanisms must be verifiable with different permission sets

### Performance Expectations
- Extremely light resource utilization suitable for legacy hardware
- Simple status checks completing within 30 seconds
- System-wide status updates at least every 5 minutes
- Support for at least 50 monitored nodes on a single monitoring server
- Immediate application of maintenance mode changes when scheduled

### Integration Points
- Email and SMS notification systems
- Simple knowledge base for resolution steps
- Basic authentication and authorization systems
- Simple scheduling system for maintenance windows
- Support for heterogeneous, often older operating systems

### Key Constraints
- Must function on hardware that is 5+ years old
- Should operate with minimal dependencies beyond Python standard library
- Must be understandable by volunteers with basic IT knowledge
- Should minimize false alarms that could overwhelm limited staff
- Must be extremely stable with minimal maintenance requirements

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Simplified Nonprofit Systems Monitor must implement the following core functionality:

1. **Accessible Status Monitoring**
   - Clear red/yellow/green status categorization for all systems
   - Plain-language system health summaries
   - Critical service availability checking
   - Simple threshold-based alerting
   - Jargon-free status reporting API

2. **Guided Issue Resolution**
   - Problem categorization and identification
   - Step-by-step resolution instructions for common issues
   - Documentation linking for more complex problems
   - Success verification steps after resolution attempts
   - Resolution history tracking for recurring issues

3. **Maintenance Management**
   - Scheduled maintenance period definition
   - Selective alert suppression during maintenance
   - Automatic maintenance mode activation and deactivation
   - Maintenance notification distribution
   - Post-maintenance verification checks

4. **Volunteer Coordination**
   - Role-based access control for monitoring functions
   - Granular permissions for different volunteer skill levels
   - Audit logging of monitoring actions taken
   - Restricted access to sensitive systems
   - Delegation and escalation workflows

5. **Resource-Efficient Operations**
   - Minimal dependency monitoring installation
   - Efficient data storage with configurable retention
   - Configurable monitoring frequency based on importance
   - Optimized resource utilization on older hardware
   - Simple backup and recovery mechanisms

## Testing Requirements

The implementation must include comprehensive tests that validate:

### Key Functionalities Verification
- Accuracy of status determination for various system conditions
- Correctness of resolution steps provided for common issues
- Effectiveness of maintenance mode in suppressing appropriate alerts
- Proper enforcement of access controls based on user roles
- Efficiency of monitoring on resource-constrained systems

### Critical User Scenarios
- Non-technical board member checking overall system status
- Volunteer troubleshooting common server issues with guided steps
- Scheduled weekend maintenance with appropriate alert suppression
- New volunteer with limited permissions assisting with monitoring
- Deploying monitoring agents to varied donated hardware

### Performance Benchmarks
- CPU and memory usage on typical nonprofit hardware
- Time to determine and report system-wide status
- Alert delivery time for critical issues
- Response time for resolution step retrieval
- Resource utilization during peak monitoring loads

### Edge Cases and Error Handling
- Behavior when monitoring target systems are unreachable
- Handling of incomplete or incorrect data from monitored systems
- Response to unauthorized access attempts
- Recovery after monitoring system restarts
- Graceful degradation on extremely resource-limited hardware

### Required Test Coverage
- 90% code coverage for core monitoring functionality
- 100% coverage for status determination algorithms
- 95% coverage for guided resolution components
- 90% coverage for maintenance mode logic
- 95% coverage for access control mechanisms

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful if it meets the following criteria:

1. Non-technical stakeholders can understand system status within 30 seconds of viewing
2. Volunteers can successfully resolve 80% of common issues by following the provided steps
3. No false alerts are generated during properly configured maintenance periods
4. Access controls correctly limit volunteer actions based on assigned roles
5. The monitoring system runs efficiently on hardware that is at least 5 years old
6. Installation requires fewer than 5 dependencies beyond the Python standard library
7. The system can be effectively maintained by staff with basic IT knowledge
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
   uv pip install -e .
   ```