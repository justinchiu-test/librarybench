# Large-Scale Simulation Task Scheduler

A concurrent task scheduler optimized for long-running scientific simulations with fault tolerance, dependency tracking, and resource management.

## Overview

The Large-Scale Simulation Task Scheduler is a specialized task execution framework designed for managing complex scientific simulations that run for extended periods across multiple computing nodes. It provides long-running job management with preemption protection, simulation dependency tracking, equipment failure resilience, resource usage forecasting, and scenario priority management to ensure efficient utilization of computational resources for scientific research.

## Persona Description

Dr. Jackson runs large-scale climate simulations requiring months of continuous computing across hundreds of nodes. His primary goal is to maximize research output by efficiently scheduling simulation tasks with checkpointing and fault tolerance.

## Key Requirements

1. **Long-Running Job Management**
   - Task scheduling system that protects critical long-running simulation jobs from preemption while allowing efficient resource sharing
   - Critical for Dr. Jackson because climate simulations can run for months, requiring protection from interruption while still allowing other users to access the system when resources aren't fully utilized

2. **Simulation Dependency Tracking**
   - Workflow management system that tracks dependencies between simulation stages and automates transitions between steps
   - Essential for managing complex multi-stage climate simulations where outputs from one stage become inputs to the next, requiring precise coordination to ensure simulation integrity and maximize throughput

3. **Equipment Failure Resilience**
   - Fault tolerance mechanisms that minimize recalculation requirements when computing resources fail during long simulations
   - Vital given the extended duration of climate simulations and the statistical likelihood of hardware failures during month-long runs, requiring strategic checkpointing and state preservation to avoid losing weeks of computation

4. **Resource Usage Forecasting**
   - Predictive tracking system for computational resource usage to support grant reporting and future resource planning
   - Important for academic accountability and future grant applications, providing detailed metrics on resource utilization efficiency and supporting capacity planning for upcoming research projects

5. **Scenario Priority Management**
   - Dynamic priority adjustment system for simulation scenarios based on preliminary result promise
   - Critical for maximizing research output by allocating more resources to simulation scenarios showing the most scientific potential based on early results, ensuring efficient use of limited computational resources

## Technical Requirements

### Testability Requirements
- Simulation workflow verification without full execution
- Accelerated testing mode for long-running jobs
- Failure injection for resilience testing
- Resource usage prediction verification

### Performance Expectations
- Support for at least 100 concurrent long-running simulations
- State preservation overhead less than 5% of simulation time
- Dependency resolution in under 10 seconds for typical workflows
- Recovery time after node failure under 5 minutes

### Integration Points
- Climate modeling software integration
- Distributed file system for simulation data
- Job scheduling interfaces for HPC environments
- Reporting tools for academic grant requirements

### Key Constraints
- Limited impact on simulation performance
- Energy efficiency considerations for long-running jobs
- Data integrity guarantees across system failures
- Support for heterogeneous computing environments

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The Large-Scale Simulation Task Scheduler should provide the following core functionality:

1. **Simulation Task Management**
   - Long-running job specification and control
   - Multi-stage simulation workflow definition
   - Resource requirement declaration
   - Runtime parameter management

2. **Dependency and Stage Control**
   - Directed acyclic graph representation of simulation stages
   - Automatic stage progression based on completion criteria
   - Dependency validation and conflict resolution
   - Parallel execution of independent simulation components

3. **Fault Tolerance and Recovery**
   - Strategic checkpoint management
   - State preservation and restoration
   - Partial result retention during failures
   - Incremental recovery strategies

4. **Resource Planning and Tracking**
   - Computational resource monitoring
   - Usage prediction and reporting
   - Grant allocation tracking
   - Efficiency optimization recommendations

5. **Prioritization and Adaptation**
   - Result promise evaluation metrics
   - Dynamic priority recalculation
   - Resource reallocation based on scientific potential
   - Scenario comparison and ranking

## Testing Requirements

### Key Functionalities to Verify
- Long-running jobs remain protected from preemption
- Simulation stages transition correctly based on dependencies
- Node failures result in minimal recalculation
- Resource usage forecasts accurately predict actual consumption
- Promising scenarios receive appropriate priority adjustments

### Critical User Scenarios
- Multi-month climate simulation with multiple dependent stages
- Hardware failure during critical simulation phase
- Resource competition between multiple research projects
- Reprioritization based on preliminary findings
- Resource usage reporting for grant renewal

### Performance Benchmarks
- Checkpoint overhead less than 5% of total simulation time
- Stage transition time less than 10 seconds
- Recovery time after node failure under 5 minutes
- Resource forecast accuracy within 10% of actual usage
- Priority recalculation within 30 seconds of new result data

### Edge Cases and Error Conditions
- Simultaneous failure of multiple compute nodes
- Corrupted checkpoint data detection and handling
- Dependency cycle detection in simulation workflow
- Resource exhaustion during peak demand
- Incompatible data formats between simulation stages

### Required Test Coverage Metrics
- 95% code coverage for core scheduling algorithms
- Complete testing of failure recovery mechanisms
- Full coverage of dependency resolution logic
- Comprehensive verification of resource tracking accuracy
- All priority adjustment pathways tested

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria

The implementation will be considered successful when:

1. Long-running simulations complete without interruption while maintaining efficient resource usage
2. Dependent simulation stages transition automatically with minimal delay
3. Node failures result in less than 15 minutes of lost computation time
4. Resource usage forecasts are accurate within 10% of actual consumption
5. Higher-potential simulation scenarios receive measurably more resources
6. The system maintains detailed accounting for grant reporting requirements
7. All tests pass, including fault tolerance and recovery scenarios
8. The system supports at least 100 concurrent long-running simulations

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