# Academic Lab Monitoring System

A specialized monitoring solution for educational computer labs that tracks classroom usage, software licenses, and student resource utilization.

## Overview

This implementation of PyMonitor is designed specifically for academic environments, enabling lab managers to organize monitoring by classroom, track software license usage, analyze lab utilization patterns, monitor student disk quotas, and detect unauthorized configuration changes to lab systems.

## Persona Description

Dr. Rodriguez oversees computer labs for a university computer science department. He needs to monitor student workstations and lab servers to preemptively address issues before they impact classes and research.

## Key Requirements

1. **Classroom Grouping Organization**
   - Implement logical grouping of systems by physical classroom location
   - Support hierarchical organization (building/floor/room/workstation)
   - Enable bulk operations and reporting by classroom group
   - Allow customizable attributes for grouping (course assignments, hardware specs)
   - Support temporary groupings for special events or specific courses
   - This is critical because educational labs are physically organized by classroom, and issues that affect an entire lab room need to be identified and addressed before classes begin.

2. **Software License Usage Tracking**
   - Monitor active usage of licensed software across lab workstations
   - Track concurrent license utilization against available license counts
   - Generate usage reports to identify underutilized or oversubscribed software
   - Alert on approaching license limits for popular applications
   - Provide historical trends to inform future license purchasing decisions
   - This is critical because academic departments have limited software budgets and need to ensure licenses are available for students during classes while optimizing costs.

3. **Lab Hours Utilization Reporting**
   - Track workstation usage patterns throughout operating hours
   - Correlate usage with scheduled class times and open lab periods
   - Generate heatmaps of peak usage times and locations
   - Identify underutilized resources and potential congestion points
   - Support semester-over-semester trend analysis
   - This is critical because academic departments need data to justify lab resources, schedule maintenance windows, and plan for future expansions or consolidations.

4. **Disk Quota Monitoring**
   - Track student storage usage across network drives and local storage
   - Monitor approaching quota limits with configurable thresholds
   - Generate reports on storage growth trends
   - Identify file types and patterns consuming excessive space
   - Support automated notifications to students approaching quotas
   - This is critical because limited shared storage resources in academic environments can be quickly depleted by student projects, potentially impacting coursework for many students.

5. **Configuration Drift Detection**
   - Monitor critical system configurations for unauthorized changes
   - Detect installation of unauthorized software or system modifications
   - Support defining standard system images and detecting deviations
   - Generate reports on systems requiring attention or reimaging
   - Track configuration changes over time with attribution when possible
   - This is critical because lab workstations are used by many students who may intentionally or accidentally modify system configurations, potentially impacting subsequent users or class activities.

## Technical Requirements

### Testability Requirements
- All components must be testable with pytest without requiring physical lab hardware
- Software license monitoring must be verifiable with simulated license usage patterns
- Usage reporting must be testable with mock usage data
- Quota monitoring must be testable with simulated file systems
- Configuration detection must be testable with predetermined configuration sets

### Performance Expectations
- Support for monitoring up to 500 workstations across multiple classrooms
- License tracking must update at minimum every 5 minutes
- Utilization analytics must aggregate data within 10 minutes of collection
- Quota monitoring must reflect changes within 15 minutes
- Configuration scans must run with minimal performance impact during active lab hours
- Historical data storage must be efficient enough to retain at least 4 academic terms

### Integration Points
- Active Directory/LDAP for student and course information
- License management systems for software entitlements
- File servers for quota monitoring
- Configuration management systems like Puppet, Chef, or Ansible
- Course scheduling systems for cross-referencing lab usage with scheduled classes
- Email/notification systems for alerts to staff and students

### Key Constraints
- Must operate in mixed Windows/Linux/macOS lab environments
- Cannot significantly impact workstation performance during active use
- Must respect student privacy according to institutional policies
- Cannot interfere with specialized lab software or hardware
- Should minimize network bandwidth utilization
- Must operate within academic budget constraints (minimal commercial dependencies)

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system should consist of these core modules:

1. **Lab Organization Module**
   - Hierarchical grouping system for lab workstations
   - Attribute-based classification and filtering
   - Group-level operations and aggregated status reporting
   - Mapping between physical locations and logical groups
   - Integration with institutional directory services

2. **License Monitoring Module**
   - Real-time tracking of software process execution
   - License pool management and availability tracking
   - Usage pattern analysis and forecasting
   - License utilization reporting and recommendations
   - Alert generation for license limit violations

3. **Usage Analytics Module**
   - Workstation utilization tracking (login/logout, active/idle)
   - Time-based analytics with customizable intervals
   - Correlation with academic schedules and events
   - Usage visualization data preparation
   - Resource utilization forecasting

4. **Storage Quota Manager**
   - File system usage monitoring across network and local storage
   - Individual and group quota tracking
   - Growth rate analysis and projections
   - File type classification and usage breakdown
   - Notification system for quota violations

5. **Configuration Management Module**
   - System configuration baseline definition
   - Regular configuration scanning and comparison
   - Drift detection and categorization
   - Remediation recommendation
   - Change history tracking

## Testing Requirements

### Key Functionalities to Verify
- Accurate organization and grouping of lab systems
- Precise tracking of software license usage
- Reliable reporting on lab utilization patterns
- Accurate monitoring of student disk quotas
- Effective detection of configuration changes

### Critical User Scenarios
- Setting up monitoring for a new computer lab
- Tracking license usage during peak class periods
- Analyzing lab utilization to optimize open hours
- Identifying students approaching storage quotas
- Detecting and addressing unauthorized system changes

### Performance Benchmarks
- Support for 500+ monitored systems without significant performance degradation
- License tracking accuracy within 2 minutes of actual usage
- Lab usage analytics processing within 10 minutes of data collection
- Quota monitoring updates within 15 minutes of file system changes
- Configuration scans completing in under 5 minutes per system

### Edge Cases and Error Conditions
- Handling network partitions between lab locations
- Managing temporary offline systems appropriately
- Correctly attributing shared computer usage in open lab hours
- Identifying false positives in configuration drift detection
- Handling academic term transitions and student turnover

### Test Coverage Metrics
- Minimum 90% code coverage across all modules
- 100% coverage of license tracking algorithms
- 100% coverage of quota calculation logic
- 100% coverage of configuration comparison functionality
- 95% coverage of grouping and organizational logic
- 90% coverage of analytics functions

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

1. **Effective Classroom Organization**
   - Systems can be logically grouped by location
   - Reporting and operations can be performed at the group level
   - Classroom-specific monitoring is easily accessible

2. **Accurate License Tracking**
   - Software license usage is accurately monitored
   - Reports clearly show utilization against available licenses
   - Alerts are generated when license limits are approached

3. **Comprehensive Utilization Analytics**
   - Lab usage patterns are clearly captured and reported
   - Peak usage times are identified
   - Data supports resource allocation decisions

4. **Proactive Quota Management**
   - Student storage usage is accurately tracked
   - Approaching quota limits are identified before they impact work
   - Storage growth trends are analyzed effectively

5. **Reliable Configuration Monitoring**
   - Unauthorized changes to lab systems are detected
   - Standard configurations are preserved
   - Systems requiring attention are clearly identified

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