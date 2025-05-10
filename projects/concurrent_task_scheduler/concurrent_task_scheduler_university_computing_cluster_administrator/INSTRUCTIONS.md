# Academic Computing Resource Scheduler

A concurrent task scheduler designed for university computing clusters that manages resource allocation across academic departments with fair-share policies and deadline awareness.

## Overview

The Academic Computing Resource Scheduler is a specialized task scheduling framework for university computing environments. It implements department quota management with unused resource reallocation, course schedule integration for teaching resources, research deadline awareness, fairness monitoring, and specialized hardware time-sharing optimization to ensure fair and efficient resource allocation across multiple academic departments.

## Persona Description

Marcus manages a shared computing cluster used by multiple academic departments with diverse computational needs. His primary goal is to fairly allocate computing resources while allowing priority overrides for urgent research and teaching needs.

## Key Requirements

1. **Department Quota Management**
   - Resource allocation system that enforces department-specific quotas while intelligently reallocating unused capacity
   - Critical for Marcus because university funding models require fair distribution of computing resources across departments based on their allocations, while ensuring maximum utilization by allowing unused capacity to flow to departments that need it

2. **Course Schedule Integration**
   - Resource reservation system that automatically allocates computing capacity based on academic course schedules
   - Essential because computational courses require guaranteed resources during class hours for student exercises, requiring seamless integration with the university's academic calendar and course timetable

3. **Research Deadline Awareness**
   - Priority adjustment mechanism that allocates additional resources to research projects approaching critical deadlines
   - Vital for academic researchers who face strict grant proposal or conference submission deadlines, allowing their computational tasks to receive increased priority as these deadlines approach

4. **Fairness Monitoring and Intervention**
   - Monitoring system that detects resource hogging and automatically intervenes to ensure equitable access
   - Critical for preventing individual users or projects from monopolizing the cluster through inefficient code or aggressive job submission, ensuring fair access for all legitimate academic needs

5. **Specialized Hardware Time-Sharing**
   - Scheduling algorithm that optimizes the allocation of limited specialized hardware (GPUs, FPGAs) across competing users
   - Important because expensive specialized computing hardware is limited, requiring intelligent time-sharing to maximize availability for courses and research that specifically require these resources

## Technical Requirements

### Testability Requirements
- Simulated workload generation for departmental usage patterns
- Course schedule scenario testing
- Deadline-driven priority verification
- Resource hogging simulation and detection testing

### Performance Expectations
- Support for at least 5,000 concurrent academic computing tasks
- Quota calculation and enforcement within 2 seconds
- Schedule-based resource transitions within 5 minutes of course start/end
- Fairness monitoring with detection under 1 minute

### Integration Points
- Academic calendar and course schedule systems
- Department quota configuration
- Research grant and project deadline tracking
- Specialized hardware monitoring and control

### Key Constraints
- Must accommodate diverse computing languages and frameworks
- Support for both interactive and batch workloads
- Limited administrative intervention required
- Clear audit trail for resource allocation decisions

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Academic Computing Resource Scheduler should provide the following core functionality:

1. **Resource Allocation and Quotas**
   - Department-based quota enforcement
   - Unused resource detection and reallocation
   - Usage accounting and reporting
   - Reservation and preemption mechanisms

2. **Schedule-Aware Management**
   - Course timetable integration
   - Advance resource reservation
   - Transitional resource management
   - Academic calendar awareness

3. **Priority and Deadline Handling**
   - Research deadline registration
   - Dynamic priority adjustment
   - Preemptive scheduling for critical deadlines
   - Priority decay for long-running tasks

4. **Fairness Enforcement**
   - Resource usage monitoring
   - Abuse detection algorithms
   - Automated intervention policies
   - User notification systems

5. **Specialized Resource Management**
   - Hardware-specific scheduling
   - Time-slicing optimization
   - Accelerator-specific job requirements
   - Utilization optimization

## Testing Requirements

### Key Functionalities to Verify
- Department quotas are enforced while allowing unused resource reallocation
- Computing resources are available for courses according to the academic schedule
- Research projects receive additional resources as deadlines approach
- Resource hogging is detected and mitigated automatically
- Specialized hardware is optimally shared across multiple users

### Critical User Scenarios
- Multiple departments competing for computing resources
- Course sessions requiring guaranteed computing capacity
- Research projects approaching publication deadlines
- Users attempting to monopolize resources
- Competing demands for limited specialized hardware

### Performance Benchmarks
- Department quota recalculation in under 2 seconds
- Course schedule transitions completed within 5 minutes
- Deadline-based priority adjustment within 1 minute of update
- Resource hogging detection within 1 minute of occurrence
- Specialized hardware utilization above 90% during peak periods

### Edge Cases and Error Conditions
- Simultaneous course sessions exceeding available capacity
- Conflicting deadline priorities between departments
- Incorrect resource usage reporting
- System failures during resource transitions
- Specialized hardware failures

### Required Test Coverage Metrics
- 95% code coverage for quota management logic
- Complete testing of schedule-based resource allocation
- Full coverage of deadline priority calculations
- All fairness monitoring algorithms verified
- Comprehensive testing of specialized hardware allocation

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Departments receive their allocated quotas with unused resources properly reallocated
2. Courses have guaranteed access to computing resources during scheduled sessions
3. Research projects successfully receive priority boosts as deadlines approach
4. Resource hogging is detected and addressed without administrative intervention
5. Specialized hardware is efficiently shared across multiple departments and users
6. The system maintains overall cluster utilization above 85%
7. All tests pass, including edge cases and error conditions
8. Resource allocation decisions are transparently logged and reportable

## Setup and Development

To set up the development environment:

```bash
# Initialize the project with uv
uv init --lib

# Install development dependencies
uv sync
```

To run the code:

```bash
# Run a script
uv run python script.py

# Run tests
uv run pytest
```