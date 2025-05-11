# Academic Computing Resource Manager

## Overview
A specialized concurrent task scheduler designed for managing shared computing clusters in academic environments. This system fairly allocates resources across multiple university departments while supporting priority overrides for urgent research and teaching needs, with particular focus on quota management, course scheduling integration, and research deadline awareness.

## Persona Description
Marcus manages a shared computing cluster used by multiple academic departments with diverse computational needs. His primary goal is to fairly allocate computing resources while allowing priority overrides for urgent research and teaching needs.

## Key Requirements

1. **Department Quota Management System**
   - Implement a sophisticated resource allocation system that enforces department quotas while dynamically reallocating unused resources to maximize cluster utilization
   - This feature is critical for Marcus as it ensures fair distribution of computing resources based on departmental funding contributions while preventing waste when allocated resources go unused
   - The system must maintain detailed usage accounting and support configurable policies for redistribution

2. **Course Schedule Integration**
   - Create a reservation system that integrates with academic course schedules to automatically reserve computing resources for teaching activities
   - This feature is essential for Marcus to ensure that computational labs and classroom exercises have guaranteed resources during scheduled class times
   - Must support recurring reservations based on semester schedules with flexibility for special events and changes

3. **Research Deadline Awareness**
   - Develop a priority adjustment mechanism that recognizes approaching research deadlines and allocates additional capacity to time-sensitive projects
   - This feature is crucial for Marcus to support researchers facing conference submissions, grant deadlines, or thesis defenses without requiring manual intervention
   - Must include verification processes to prevent abuse while enabling legitimate urgent research needs

4. **Fairness Monitoring and Enforcement**
   - Implement a monitoring system that detects and automatically intervenes when users or groups monopolize resources beyond their fair allocation
   - This feature is vital for Marcus to maintain equitable access to the cluster, especially for smaller departments or junior researchers who might otherwise be overshadowed
   - Must include configurable policies for defining "fair share" and appropriate interventions

5. **Specialized Hardware Management**
   - Create an intelligent scheduling system for specialized hardware (GPUs, FPGAs) that optimizes time-sharing and allocation based on workload characteristics
   - This feature is important for Marcus because specialized computing hardware is expensive and limited, requiring careful allocation to maximize research output
   - Must include support for reservations, fractional allocations, and priority adjustments

## Technical Requirements

### Testability Requirements
- All components must be independently testable with well-defined interfaces
- System must support simulation of departmental usage patterns without requiring actual workloads
- Test coverage should exceed 85% for all resource allocation and scheduling components
- Tests must validate fair allocation under various demand scenarios

### Performance Expectations
- Support for at least 1,000 concurrent jobs across multiple departments
- Scheduling decisions must complete in under 500ms even with complex quota rules
- System should achieve at least 90% resource utilization under normal conditions
- Quota enforcement and reallocation should operate with minimal overhead

### Integration Points
- Integration with common job schedulers (Slurm, PBS, HTCondor)
- Support for course management and calendar systems
- Interfaces for departmental reporting and chargeback systems
- Compatibility with cluster monitoring and management tools

### Key Constraints
- IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.
- The system must maintain complete fairness while maximizing resource utilization
- All allocation decisions must be fully auditable for departmental accountability
- Must operate in heterogeneous hardware environments
- System must be resilient to individual node failures

## Core Functionality

The Academic Computing Resource Manager must provide:

1. **Resource Quota Definition and Enforcement**
   - Mechanism for defining departmental allocations and usage limits
   - Enforcement of quotas during resource contention periods
   - Dynamic reallocation of unused resources with appropriate policies

2. **Scheduling and Reservation**
   - Support for both advance reservations and immediate resource requests
   - Integration with academic schedules for teaching resource allocation
   - Handling of recurring reservations with exception management

3. **Priority Management and Preemption**
   - Configurable priority levels for different user types and activities
   - Deadline-based priority adjustments for research projects
   - Fair-share algorithms that balance historical usage against allocations

4. **Usage Monitoring and Reporting**
   - Collection of detailed usage metrics by department, research group, and user
   - Analysis of utilization patterns to identify optimization opportunities
   - Generation of reports for departmental chargeback and planning

5. **Hardware Specialization**
   - Intelligent allocation of specialized computing resources
   - Time-sharing optimization for expensive hardware components
   - Job-to-hardware matching based on workload characteristics

## Testing Requirements

### Key Functionalities to Verify
- Quota enforcement correctly limits resource usage during contention
- Unused resource reallocation maintains fairness while improving utilization
- Course schedule integration properly reserves resources for teaching activities
- Research deadline awareness appropriately adjusts priorities for time-sensitive projects
- Fairness monitoring correctly identifies and addresses resource monopolization

### Critical Scenarios to Test
- Handling of competing high-priority research projects near deadlines
- Resource allocation during peak periods (end of semester, conference deadlines)
- Management of specialized hardware requests exceeding availability
- Proper handling of emergency teaching needs or schedule changes
- Response to simulated hardware failures or maintenance events

### Performance Benchmarks
- Scheduling overhead should not exceed 1% of total compute time
- System should achieve at least 90% resource utilization under normal conditions
- Priority adjustments should be applied within 5 minutes of deadline information updates
- Quota enforcement should have minimal impact on job launch latency

### Edge Cases and Error Conditions
- Handling of conflicts between course reservations and deadline-driven research
- Correct behavior when total demand far exceeds available resources
- Recovery from scheduling database corruption or inconsistencies
- Proper management of abandoned or orphaned jobs
- Graceful degradation during partial cluster failures

### Required Test Coverage
- Minimum 85% line coverage for all scheduling and allocation components
- Comprehensive integration tests for quota enforcement and reallocation
- Performance tests simulating peak usage periods
- Fairness validation under various departmental demand patterns

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

The implementation will be considered successful if:

1. Department quota management maintains fairness while achieving at least 90% resource utilization
2. Course schedule integration successfully reserves resources for 100% of scheduled classes
3. Research deadline awareness appropriately prioritizes time-sensitive projects
4. Fairness monitoring prevents any user or group from monopolizing resources
5. Specialized hardware management achieves at least 85% utilization of GPUs and other limited resources

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

## Setup Instructions

1. Setup a virtual environment using UV:
   ```
   uv venv
   source .venv/bin/activate
   ```

2. Install the project in development mode:
   ```
   uv pip install -e .
   ```

3. CRITICAL: Run tests with pytest-json-report to generate pytest_results.json:
   ```
   pip install pytest-json-report
   pytest --json-report --json-report-file=pytest_results.json
   ```

REMINDER: Generating and providing pytest_results.json is a critical requirement for project completion.