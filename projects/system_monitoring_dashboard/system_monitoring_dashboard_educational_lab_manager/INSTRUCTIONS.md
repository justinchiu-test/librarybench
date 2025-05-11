# Academic Computer Lab Monitoring System

A specialized monitoring solution designed for university computer science departments to track, analyze, and proactively manage computer lab resources.

## Overview

The Academic Computer Lab Monitoring System is a tailored implementation of the PyMonitor system that focuses on the unique needs of educational environments. It enables lab managers to track student workstation usage, monitor specialized software availability, analyze utilization patterns, and detect unauthorized configuration changes to ensure labs remain consistently available for classes and research activities.

## Persona Description

Dr. Rodriguez oversees computer labs for a university computer science department. He needs to monitor student workstations and lab servers to preemptively address issues before they impact classes and research.

## Key Requirements

1. **Classroom Grouping Organization** - Implement a flexible system that organizes monitoring by physical location and course requirements. This is critical for Dr. Rodriguez because it allows him to manage different labs with varying hardware configurations and software installations, prioritizing attention based on current and upcoming class schedules.

2. **Software License Usage Tracking** - Develop functionality to monitor the utilization of specialized software licenses across lab workstations. This is essential because the department has limited, expensive licenses for specialized software, and Dr. Rodriguez needs to ensure availability for courses that require these applications while optimizing license allocation.

3. **Lab Hours Utilization Reporting** - Create a system to track and analyze patterns in student computer usage across different times and locations. Dr. Rodriguez needs this data to make informed decisions about lab availability hours, resource allocation, and capacity planning based on actual usage patterns throughout the academic year.

4. **Disk Quota Monitoring** - Implement disk usage tracking for student accounts across shared storage resources. This is crucial because students working on programming projects and research can quickly fill shared storage, potentially disrupting classes and other students' work if not proactively managed.

5. **Configuration Drift Detection** - Develop functionality to identify unauthorized changes to lab systems compared to approved baseline configurations. This capability is important because lab workstations frequently experience configuration changes from student use, and Dr. Rodriguez needs to identify which machines need restoration to standard configurations before classes.

## Technical Requirements

### Testability Requirements
- All monitoring components must be testable with pytest
- License monitoring must support mocked license servers
- Usage pattern analysis must be testable with synthetic usage data
- Configuration checking must verify against sample baselines without requiring actual drift

### Performance Expectations
- Minimal impact on lab workstation performance during active student use
- Ability to handle simultaneous monitoring of up to 200 workstations
- Quick scan of disk quotas across networked storage (complete in under 5 minutes)
- Configuration drift detection that completes within 10 minutes for a 30-machine lab

### Integration Points
- Integration with common license servers (FlexLM, etc.)
- Support for networked file systems for quota monitoring
- Compatibility with Active Directory or LDAP for user account information
- Interface with system imaging or configuration management tools
- Support for scheduling systems to correlate with class timetables

### Key Constraints
- Must not interfere with student work during classes
- Should operate with minimal privileges on student workstations
- Must accommodate heterogeneous lab environments (different hardware/software configurations)
- Must respect student privacy while collecting necessary utilization data
- Must support multiple operating systems (Windows, Linux, macOS) commonly found in academic environments

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Academic Computer Lab Monitoring System must implement the following core functionality:

1. **Lab Organization and Management**
   - Logical grouping of computers by physical lab, course requirements, or hardware capabilities
   - Tagging system for associating machines with courses and requirements
   - Scheduling awareness to prioritize monitoring based on current and upcoming classes
   - Summary views of lab status organized by physical or logical groupings
   - Resource allocation tracking across different lab environments

2. **License Utilization Monitoring**
   - Connection to license servers to track current usage and availability
   - Historical tracking of license utilization patterns
   - Course-correlated license requirements and availability forecasting
   - Alert mechanisms for license exhaustion before scheduled classes
   - License usage optimization recommendations

3. **Student Usage Analytics**
   - Anonymous tracking of workstation utilization by time and location
   - Peak usage time identification and trending
   - Correlation between class schedules and actual usage patterns
   - Resource demand forecasting based on historical patterns
   - Underutilized resource identification for potential reallocation

4. **Storage Quota Management**
   - Individual and aggregate disk usage monitoring
   - Quota threshold alerting before critical levels are reached
   - Growth rate analysis and capacity planning
   - Identification of unusual storage consumption patterns
   - Historical usage trends correlated with academic calendar

5. **System Configuration Compliance**
   - Baseline configuration definition and storage
   - Scheduled and on-demand configuration verification
   - Detailed reporting of configuration drift with specific changes
   - Prioritization of critical vs. non-critical configuration differences
   - Integration with system restoration or remediation processes

## Testing Requirements

The implementation must include comprehensive tests that validate:

### Key Functionalities Verification
- Accuracy of license usage tracking compared to actual license servers
- Precision of disk quota measurements across different storage systems
- Reliability of configuration drift detection with various types of changes
- Consistency of usage pattern analysis with synthetic data
- Effectiveness of lab grouping and organization mechanisms

### Critical User Scenarios
- Preparing labs for upcoming classes with specific software requirements
- Identifying and addressing storage quota issues before they impact classes
- Detecting and remediating unauthorized system configuration changes
- Analyzing lab usage patterns to optimize availability hours
- Ensuring license availability for specialized software during peak usage periods

### Performance Benchmarks
- Time to scan and report configuration drift across a full lab
- Speed of license status checks across multiple license servers
- Efficiency of disk quota calculations for large shared storage systems
- Resource impact of monitoring agents on active workstations
- Scalability testing with increasing numbers of monitored systems

### Edge Cases and Error Handling
- Behavior when license servers are unavailable
- Handling of network storage connectivity issues
- Graceful degradation during partial monitoring system failure
- Recovery from interrupted configuration scans
- Handling of corrupt or unexpected configuration states

### Required Test Coverage
- 90% code coverage for core monitoring components
- 100% coverage for license monitoring logic
- 95% coverage for configuration comparison algorithms
- 90% coverage for storage quota calculation
- 90% coverage for usage pattern analysis

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful if it meets the following criteria:

1. Lab workstations can be effectively organized and monitored by location, course requirements, and hardware capabilities
2. Software license availability issues are detected at least 15 minutes before scheduled classes that require those licenses
3. Student usage patterns are accurately captured and analyzed to identify peak usage times with 95% accuracy
4. Disk quota issues are identified and reported before they impact class activities
5. Configuration drift is detected with at least 98% accuracy compared to baseline configurations
6. The system scales effectively to monitor at least 200 workstations simultaneously
7. Resource impact on monitored workstations is negligible during active student use
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