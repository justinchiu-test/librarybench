# Research Pipeline Orchestrator for Data Science Teams

## Overview
A specialized concurrent task scheduler designed specifically for data science teams running complex machine learning pipelines. This system optimizes computational resource allocation across multiple research projects while ensuring critical deadlines are met, with a focus on intelligent prioritization, resource budgeting, and failure recovery.

## Persona Description
Dr. Elisa manages a team of data scientists who run complex machine learning pipelines that combine data preprocessing, model training, and evaluation steps. Her primary goal is to optimize computational resource usage across multiple team projects while ensuring critical research deadlines are met.

## Key Requirements

1. **Research Project Prioritization System**
   - Implement intelligent prioritization that automatically adjusts team resource allocation based on project deadlines, importance, and current progress
   - This feature is critical as it allows Dr. Elisa to ensure that high-priority research initiatives receive appropriate computational resources while still maintaining fair allocation for all team projects
   - The system must dynamically re-prioritize as deadlines approach or project parameters change

2. **Computational Budget Enforcement**
   - Create a resource allocation system with configurable caps per project/user that prevents any single project from monopolizing computational resources
   - This feature is essential for Dr. Elisa to manage finite computational resources across multiple competing research projects while ensuring equitable access for all team members
   - Must support both hard caps (never exceed) and soft caps (can exceed temporarily if resources are available)

3. **Experiment Checkpointing and Recovery**
   - Implement automatic checkpointing of machine learning experiments with intelligent resumption capabilities after system failures
   - This feature is crucial for Dr. Elisa's team as long-running ML experiments are particularly vulnerable to infrastructure failures, and restarting from scratch wastes valuable computational resources and research time
   - Must minimize checkpoint overhead while ensuring experiment integrity

4. **Specialized Hardware Allocation**
   - Develop an intelligent scheduler for GPU and other specialized hardware resources that optimizes training job placement and execution
   - This feature is vital as specialized computing hardware is expensive and limited, requiring careful allocation to maximize research output and minimize idle time
   - Must understand the specific hardware requirements of different ML frameworks and model architectures

5. **Pipeline Visualization and Monitoring**
   - Create a programmatic API for monitoring pipeline execution, showing actual vs. expected completion times for each stage and overall project
   - This feature is essential for Dr. Elisa to track research progress, identify bottlenecks, and make informed decisions about resource allocation and project timelines
   - Must support both real-time monitoring and historical analysis

## Technical Requirements

### Testability Requirements
- All components must be independently testable with clear interfaces
- Must support mocking of resource-intensive operations for testing
- Pipeline execution must be deterministic and reproducible in test environments
- Test coverage should be at least 85% for all core functionality

### Performance Expectations
- Support for at least 100 concurrent pipeline executions across team projects
- Scheduling decisions must complete in under 100ms even with complex dependency graphs
- Checkpointing overhead should not exceed 5% of total computation time
- System must make efficient use of available computational resources with minimal idle time

### Integration Points
- Integration with common ML frameworks (PyTorch, TensorFlow, scikit-learn)
- Support for distributed training frameworks (Horovod, Ray)
- Ability to interface with job queuing systems (Slurm, PBS)
- Programmatic API for external monitoring and analysis

### Key Constraints
- IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.
- The system must maintain data integrity and experiment reproducibility
- Must operate efficiently in a shared computing environment
- All operations should be non-blocking where possible
- System must be resilient to individual task failures

## Core Functionality

The Research Pipeline Orchestrator must provide:

1. **Task Definition and Pipeline Construction**
   - A declarative API for defining tasks with their resource requirements and dependencies
   - Support for constructing complex pipelines with branching, conditional execution, and dynamic task generation
   - Task definitions should support metadata relevant to data science workflows (experiment parameters, dataset information)

2. **Resource-Aware Scheduling**
   - Intelligent scheduling that accounts for task priorities, deadlines, and resource requirements
   - Efficient allocation of specialized resources (GPUs, high-memory nodes)
   - Fair-sharing algorithms that balance resources across projects while respecting priorities

3. **Fault Tolerance and Recovery**
   - Automatic checkpointing of computational state at configurable intervals
   - Intelligent recovery from failures with minimal recomputation
   - Failure isolation to prevent cascade failures across the pipeline

4. **Runtime Monitoring and Adaptation**
   - Collection of runtime metrics and execution statistics
   - Dynamic reallocation of resources based on actual progress versus expectations
   - APIs for querying system state and receiving notifications about significant events

5. **Budget Management**
   - Tracking of resource usage against configured budgets
   - Enforcement of resource limits with configurable policies
   - Support for borrowing/lending resources between projects with permission

## Testing Requirements

### Key Functionalities to Verify
- Task dependency resolution correctly orders task execution
- Priorities correctly influence resource allocation
- Budget enforcement properly limits resource consumption
- Checkpointing correctly saves and restores execution state
- Pipeline execution correctly handles task failures and retries

### Critical Scenarios to Test
- Handling of complex dependency graphs with hundreds of tasks
- Response to resource contention between high-priority projects
- Recovery from simulated hardware failures during execution
- Handling of long-running pipelines with multiple stages
- Dynamic reprioritization as deadlines approach

### Performance Benchmarks
- Scheduling overhead should remain below 5% of total computation time
- System should achieve at least 90% resource utilization under normal conditions
- Checkpoint/restore operations should complete in under 30 seconds for typical workloads
- System should scale linearly with number of workers up to at least 32 cores

### Edge Cases and Error Conditions
- Handling of cyclic dependencies in task graphs
- Graceful degradation under extreme resource contention
- Recovery from corrupted checkpoints
- Handling of tasks with excessive resource demands
- Proper cleanup after catastrophic failures

### Required Test Coverage
- Minimum 85% line coverage for core functionality
- 100% coverage of error handling and recovery paths
- Performance tests for all resource-intensive operations
- Integration tests covering end-to-end pipeline execution

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

1. All resource allocation decisions respect project priorities and budget constraints
2. Experiment checkpointing correctly saves and restores state with minimal overhead
3. Specialized hardware allocation achieves at least 90% utilization
4. Pipeline monitoring accurately reflects execution state and progress
5. The system can handle at least 100 concurrent pipelines across multiple projects

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