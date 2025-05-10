# Research Pipeline Task Scheduler

A concurrent task scheduling framework optimized for data science and machine learning workflows with research project prioritization and resource management.

## Overview

The Research Pipeline Task Scheduler is a specialized version of a concurrent task scheduler that focuses on managing computational resources across multiple data science projects. It enables automated resource allocation based on project priorities, enforces computational budgets, handles failures gracefully through checkpointing, optimizes specialized hardware usage, and provides visualization of pipeline progress and completion estimates.

## Persona Description

Dr. Elisa manages a team of data scientists who run complex machine learning pipelines that combine data preprocessing, model training, and evaluation steps. Her primary goal is to optimize computational resource usage across multiple team projects while ensuring critical research deadlines are met.

## Key Requirements

1. **Research Project Prioritization System**
   - A priority management system that automatically adjusts resource allocation based on project importance and deadlines
   - Critical for Dr. Elisa's team to ensure important research projects get the necessary computational resources without manual intervention while still ensuring all projects have access to computing resources

2. **Computational Budget Enforcement**
   - Resource cap mechanism that limits CPU/memory/GPU usage per project or user based on predefined budgets
   - Essential for preventing resource monopolization by individual team members or projects, allowing fair distribution of limited computational resources across multiple concurrent research initiatives 

3. **Experiment Checkpointing and Resumption**
   - Automated saving of intermediate computation states and the ability to resume from the last valid checkpoint after failures
   - Vital for long-running machine learning training jobs where hardware failures or preemption could otherwise result in days of lost computation time

4. **Specialized Hardware Allocation**
   - Intelligent scheduling for GPU and other specialized hardware resources that optimizes job characteristics to hardware capabilities
   - Necessary for efficient utilization of expensive GPU resources, ensuring the right types of training jobs are matched to the appropriate hardware accelerators

5. **Pipeline Visualization and Timing**
   - Visual representation of task dependencies showing actual vs. expected completion times for pipeline stages
   - Critical for tracking progress across complex multi-stage ML pipelines and identifying bottlenecks or resource constraints in real-time

## Technical Requirements

### Testability Requirements
- All scheduler components must be individually testable
- Task execution must support deterministic mocking for predictable test outcomes
- Scheduling decisions must be traceable and explainable for debugging
- Time-dependent operations must support artificial acceleration for testing

### Performance Expectations
- Scheduling decisions must complete in under 100ms for up to 1,000 pending tasks
- Support for at least 100 concurrent active tasks across multiple projects
- Checkpoint operations must not impact task execution time by more than 5%
- Priority recalculation should occur within 1 second of deadline changes

### Integration Points
- Python API for task definition and submission
- Resource monitoring integration for CPU, memory, and GPU usage
- Storage backend for checkpoints with pluggable providers
- Event hooks for external scheduling policy integration

### Key Constraints
- The implementation must be thread-safe and process-safe
- No persistent database requirements (file-based storage only)
- All visualizations must be exportable as static data for external rendering
- The system should operate without elevated system privileges

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Research Pipeline Task Scheduler should provide the following core functionality:

1. **Task Definition and Dependency Management**
   - Python API for defining computational tasks with input/output specifications
   - Support for directed acyclic graphs (DAGs) to represent pipeline dependencies
   - Task grouping capabilities to represent multi-stage ML pipelines

2. **Resource-Aware Scheduling**
   - Dynamic priority calculation based on project importance and deadlines
   - Resource usage tracking and enforcement of computational budgets
   - Specialized hardware matching for GPU-accelerated tasks

3. **Execution and Monitoring**
   - Concurrent task execution with appropriate resource isolation
   - Real-time monitoring of task progress and resource consumption
   - Prediction of completion times based on historical performance

4. **Fault Tolerance**
   - Automatic checkpointing of intermediate computation states
   - Task retry mechanisms with configurable backoff strategies
   - Failed task handling with appropriate cleanup

5. **Reporting and Analysis**
   - Pipeline execution statistics collection
   - Visualization data for task dependencies and execution timelines
   - Resource utilization reports for retrospective analysis

## Testing Requirements

### Key Functionalities to Verify
- Project prioritization correctly allocates resources based on configured importance
- Computational budgets effectively limit resource usage per project/user
- Checkpointing successfully preserves and restores task state after failures
- GPU-intensive tasks are correctly scheduled on appropriate hardware
- Timeline visualizations accurately represent task dependencies and timing

### Critical User Scenarios
- Multiple simultaneous ML pipelines with differing priorities competing for resources
- Dynamic reprioritization when project deadlines change
- Hardware failure during long-running tasks with successful resumption
- Budget exhaustion handling and appropriate task queuing
- Specialized hardware allocation under constrained availability

### Performance Benchmarks
- Scheduling overhead remains under 5% of total computation time
- Checkpoint/resume cycle completes in under 30 seconds for typical workloads
- Priority recalculation completes in under 1 second for the entire system
- System handles at least 1,000 pending tasks with sub-100ms scheduling decisions
- Resource allocation remains optimal within 5% of theoretical maximum utilization

### Edge Cases and Error Conditions
- Circular dependencies in pipeline definitions
- Resource exhaustion with proper degradation
- Corrupted checkpoint data detection and recovery
- Priority conflicts with clear resolution
- Hardware failure during checkpointing

### Required Test Coverage Metrics
- Minimum 90% line coverage for core scheduling logic
- All priority calculation code paths must be tested
- Full coverage of resource allocation decision tree
- Complete testing of checkpoint/resume lifecycle
- All error and exception paths must be verified

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Research projects receive computational resources proportional to their priority settings
2. No user or project exceeds their allocated resource budget
3. Failed tasks successfully resume from checkpoints with minimal repeated computation
4. Specialized hardware utilization exceeds 80% during peak periods
5. Pipeline visualizations accurately predict completion times within 15% of actual runtime
6. Multiple concurrent ML pipelines execute with optimal resource utilization
7. System handles deadline changes with appropriate resource reallocation
8. All tests pass, including edge cases and error conditions

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