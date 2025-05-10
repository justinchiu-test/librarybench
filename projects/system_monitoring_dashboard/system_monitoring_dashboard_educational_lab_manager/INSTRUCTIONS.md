# Academic Computer Lab Monitoring System

## Overview
A specialized monitoring system designed for university computer labs that organizes systems by physical location and course requirements, tracks software license usage, monitors lab utilization patterns, enforces disk quotas, and detects unauthorized configuration changes to ensure reliable operation for classes and student research.

## Persona Description
Dr. Rodriguez oversees computer labs for a university computer science department. He needs to monitor student workstations and lab servers to preemptively address issues before they impact classes and research.

## Key Requirements

1. **Classroom-Based System Grouping**
   - Implement a monitoring structure that organizes systems by physical classroom location and course requirements
   - This is critical because lab managers need to quickly identify and resolve issues in specific classrooms before they impact scheduled classes
   - The system must support hierarchical organization and flexible grouping to align with physical lab layouts and course assignments

2. **Software License Usage Tracking**
   - Create a license monitoring component that tracks usage of specialized academic software with limited licenses
   - This is essential because academic departments have limited software budgets and need to ensure license availability for scheduled classes
   - Tracking must identify which users/systems are consuming licenses and for how long to optimize license allocation

3. **Lab Utilization Reporting**
   - Develop comprehensive lab usage analytics that reveal patterns in when and how students use computing resources
   - This is vital because understanding usage patterns helps optimize lab hours, justify resource allocation, and schedule maintenance windows
   - Reports must correlate usage with course schedules, time of day, and academic calendar events

4. **Student Disk Quota Monitoring**
   - Implement storage monitoring that tracks individual and aggregate student disk usage against defined quotas
   - This is important because shared storage resources must be fairly allocated to prevent students from consuming excessive space and impacting others
   - The system must identify approaching quota limits before they become critical and affect student work

5. **Configuration Drift Detection**
   - Create a system that identifies unauthorized changes to lab computer configurations and software installations
   - This is crucial because lab environments must maintain consistent configurations to support coursework and prevent academic integrity issues
   - Detection must compare current system states against approved baseline configurations to identify discrepancies

## Technical Requirements

- **Testability Requirements**
  - All components must have unit tests with minimum 85% code coverage
  - Mock objects must simulate student workstations and lab server environments
  - Test fixtures must generate synthetic usage data for reporting validation
  - Integration tests must verify behavior across different lab configurations
  - Test parameterization must validate different classroom layouts and groupings

- **Performance Expectations**
  - Monitoring must not impact performance of workstations during active student use
  - License tracking must update within 30 seconds of license checkout/return
  - Lab utilization data must be processed and available for reporting within 5 minutes
  - Storage quota monitoring must refresh at least every 15 minutes
  - Configuration checks must complete within 10 minutes across a 50-machine lab

- **Integration Points**
  - Academic calendar integration for correlating usage with course schedules
  - License server integration for popular academic software (MATLAB, SAS, SPSS, etc.)
  - User authentication integration with university directory services
  - File system access for storage quota monitoring
  - OS-level integration for configuration state analysis

- **Key Constraints**
  - Must support heterogeneous environments (Windows/Mac/Linux) common in academic settings
  - Cannot significantly impact workstation performance during active classroom use
  - Must operate within university network security policies and restrictions
  - Must scale to handle at least 200 workstations across multiple physical locations
  - Storage and processing overhead must be minimal on monitored systems

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The system must provide:

1. **Lab Structure Management**
   - Flexible definition of classroom locations and groupings
   - Assignment of workstations to specific rooms and course allocations
   - Dynamic regrouping based on changing class requirements
   - Status aggregation at room, course, and department levels
   - Maintenance scheduling aligned with physical locations

2. **License Utilization Tracking**
   - Real-time monitoring of license checkouts and returns
   - License usage correlation with user identities and course activities
   - Historical license utilization patterns and peak usage periods
   - License saturation alerts when approaching 100% utilization
   - Recommendations for optimal license quantity based on usage patterns

3. **Usage Analytics Engine**
   - Collection of system usage metrics (login duration, active vs. idle time)
   - Correlation of usage with academic schedule and calendar
   - Identification of peak usage periods and underutilized resources
   - Long-term trend analysis for capacity planning
   - Anomaly detection for unusual usage patterns

4. **Storage Quota Enforcement**
   - Individual and aggregate storage usage tracking
   - Proactive alerts for approaching quota limits
   - Historical storage growth tracking
   - Identification of storage-intensive users and applications
   - Recommendations for quota adjustments based on course requirements

5. **Configuration Compliance System**
   - Definition of baseline configurations for different lab environments
   - Regular comparison of current state against approved baselines
   - Detailed reporting of unauthorized changes and modifications
   - Automatic or guided remediation recommendations
   - Compliance history tracking across academic terms

## Testing Requirements

- **Key Functionalities to Verify**
  - Accuracy of classroom grouping and status aggregation
  - Precision of license usage tracking and reporting
  - Reliability of usage pattern detection and reporting
  - Consistency of disk quota monitoring and alerting
  - Effectiveness of configuration drift detection

- **Critical User Scenarios**
  - Preparing labs for an upcoming class with specific software requirements
  - Investigating license unavailability during a scheduled lab session
  - Analyzing lab usage patterns to justify additional resources or extended hours
  - Identifying students approaching disk quotas before they impact coursework
  - Detecting and remediating unauthorized software installations

- **Performance Benchmarks**
  - Agent impact must be less than 2% CPU and 50MB RAM on student workstations
  - License status changes must be detected within 30 seconds
  - Utilization reports must process and analyze data for 100 systems in under 2 minutes
  - Quota monitoring must scan and report on 1TB of student storage within 10 minutes
  - Configuration checks must complete for a single system in under 2 minutes

- **Edge Cases and Error Conditions**
  - System behavior when lab workstations are repeatedly rebooted by students
  - Recovery after network partitioning between monitoring components
  - Handling of abrupt system shutdowns during monitoring
  - Management of conflicting course requirements for shared lab spaces
  - Behavior during academic calendar transitions (semester start/end)

- **Test Coverage Requirements**
  - Minimum 85% code coverage across all components
  - 100% coverage for critical license tracking and quota monitoring modules
  - All public APIs must have interface tests with multiple parameter variations
  - Error handling paths must be fully tested with simulated failure conditions
  - Multi-platform compatibility must be verified through specific test cases

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

A successful implementation will:

1. Accurately organize and display system status by classroom location and course allocation
2. Track software license usage with at least 98% accuracy and detect license saturation before it impacts classes
3. Generate utilization reports that identify peak usage periods and correlate with academic schedules
4. Monitor student disk quotas and provide alerts at least 24 hours before quotas are reached
5. Detect at least 95% of unauthorized configuration changes within 12 hours of occurrence
6. Support at least 200 workstations across multiple physical lab locations
7. Maintain monitoring agent overhead below 2% CPU and 50MB RAM during active student use
8. Achieve 85% test coverage across all modules

## Setup and Development

To set up your development environment:

1. Use `uv init --lib` to initialize the project structure and setup the virtual environment
2. Install dependencies with `uv sync`
3. Run the application with `uv run python your_script.py`
4. Run tests with `uv run pytest`
5. Format code with `uv run ruff format`