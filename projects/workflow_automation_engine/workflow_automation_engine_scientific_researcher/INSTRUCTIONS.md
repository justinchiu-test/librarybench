# Experimental Workflow Engine for Scientific Research

A specialized workflow automation engine for computational experiments with parameter variations, metadata tracking, and reproducibility packaging.

## Overview

This project implements a Python library for defining, executing, and managing computational research workflows with support for parameter sweep automation, extensive metadata capture, resource optimization, result visualization, and reproducibility packaging. The system is specifically designed to help scientific researchers automate experiments while maintaining complete records for reproducibility.

## Persona Description

Dr. Chen conducts computational experiments that involve multiple processing steps and parameter variations. He needs to automate experiment workflows while tracking results and computational environments for reproducibility.

## Key Requirements

1. **Parameter Sweep Automation**: Implement functionality to execute workflows across multiple configuration combinations.
   - Critical for Dr. Chen to explore the parameter space efficiently without manual intervention.
   - System should automatically generate and execute workflow variants with different parameter combinations, tracking results for each variation.

2. **Experiment Metadata Capture**: Create comprehensive recording of all inputs, environments, and execution details.
   - Essential for Dr. Chen to maintain scientific rigor and enable reproduction of results.
   - Must capture all aspects of the experimental environment, including code versions, input data, parameters, and system configuration.

3. **Computational Resource Optimization**: Develop scheduling of intensive tasks during off-peak hours.
   - Vital for Dr. Chen to maximize resource utilization and minimize interference with other researchers' work.
   - System should intelligently schedule tasks based on resource requirements and availability.

4. **Result Visualization**: Implement automatic generation of plots and dashboards from experimental outputs.
   - Necessary for Dr. Chen to quickly analyze and compare results from different parameter combinations.
   - Should produce standardized visualizations for key metrics across parameter variations.

5. **Reproducibility Packaging**: Create capture of all workflow elements for future replication.
   - Critical for Dr. Chen to share experiments with colleagues and document methods for publication.
   - Must package code, configuration, environment specifications, and execution steps in a format that can be easily shared and executed.

## Technical Requirements

### Testability Requirements
- All components must be fully testable with pytest without requiring actual computation resources
- Test fixtures should provide sample experimental setups with known outcomes
- Parameter sweep logic must be verifiable with deterministic test cases
- Metadata capture should be validated for completeness and accuracy
- Reproducibility packages must be testable for integrity and completeness

### Performance Expectations
- Support for parameter sweeps with at least 1,000 combinations
- Ability to schedule and manage long-running experiments (days to weeks)
- Minimal overhead for metadata capture (<1% of computation time)
- Efficient resource utilization during parallel execution
- Visualization generation in under 30 seconds for typical result sets

### Integration Points
- High-performance computing (HPC) schedulers and resource managers
- Scientific computing libraries and domain-specific tools
- Data storage systems for experimental results
- Visualization libraries and reporting tools
- Version control systems for code and configuration

### Key Constraints
- No UI components - all functionality must be accessible via Python API
- Must work in environments with limited network connectivity
- Storage requirements for metadata must be reasonable relative to experimental data
- System should function without administrative privileges
- Must support both local execution and HPC environments

## Core Functionality

The system must provide a Python library that enables:

1. **Experimental Workflow Definition**: A programmatic interface for defining scientific workflows with:
   - Task dependencies and execution order
   - Parameter spaces for automated exploration
   - Resource requirements and constraints
   - Result specifications and success criteria
   - Metadata capture requirements

2. **Parameter Sweep Execution**: An execution engine that:
   - Generates workflow variants for all parameter combinations
   - Manages execution across combinations efficiently
   - Tracks results and metadata for each combination
   - Provides status monitoring and progress reporting
   - Implements appropriate parallelization strategies

3. **Metadata Tracking System**: A comprehensive recording system that:
   - Captures all environmental factors (libraries, versions, etc.)
   - Records all input parameters and data sources
   - Tracks execution timing and resource utilization
   - Documents all generated outputs and artifacts
   - Maintains execution provenance and dependencies

4. **Resource Management**: An intelligent scheduling system that:
   - Analyzes task resource requirements
   - Schedules execution based on resource availability
   - Implements execution policies (off-peak, priority, etc.)
   - Monitors and reports resource utilization
   - Adapts to changing resource availability

5. **Result Analysis Tools**: A suite of tools that:
   - Automatically generates standard visualizations
   - Creates comparative views across parameter variations
   - Produces statistical summaries of results
   - Identifies optimal parameter combinations
   - Exports results in publication-ready formats

6. **Reproducibility Packaging**: A system that:
   - Captures complete workflow definitions and configurations
   - Records exact environmental requirements
   - Packages all necessary code and dependencies
   - Creates executable reproduction instructions
   - Verifies package completeness and integrity

## Testing Requirements

### Key Functionalities to Verify
- Correct execution of workflow tasks with all parameter combinations
- Complete and accurate metadata capture for all experimental factors
- Proper scheduling based on resource policies and availability
- Accurate visualization generation for various result types
- Complete and functional reproducibility packages

### Critical User Scenarios
- Parameter sweep experiment with interdependent variables
- Long-running computation with intermediate result checkpointing
- Resource-intensive workflow scheduled during off-peak hours
- Comparative analysis across multiple parameter variations
- Recreation of experiment from reproducibility package

### Performance Benchmarks
- Support parameter sweeps with 1,000+ combinations without memory issues
- Metadata storage overhead less than 5% of result data size
- Resource scheduling efficiency resulting in at least 90% utilization
- Visualization generation in under 30 seconds for standard result sets
- Reproducibility package creation in under 60 seconds

### Edge Cases and Error Conditions
- Handling of failed executions within parameter sweeps
- Recovery from node failures in distributed computations
- Proper metadata capture for prematurely terminated experiments
- Graceful degradation when resource constraints cannot be met
- Package verification when environment cannot be exactly replicated

### Required Test Coverage Metrics
- Minimum 90% line coverage for core workflow engine
- 100% coverage of parameter sweep generation logic
- 100% coverage of metadata capture mechanisms
- All visualization generation paths must be tested
- Complete verification of reproducibility package integrity

## Success Criteria

The implementation will be considered successful if it demonstrates:

1. The ability to define and execute scientific workflows across multiple parameter combinations
2. Comprehensive metadata capture that enables full experiment reproducibility
3. Intelligent resource scheduling that optimizes utilization
4. Automatic visualization generation that facilitates result analysis
5. Reproducibility packaging that enables accurate experiment recreation
6. All tests pass with the specified coverage metrics
7. Performance meets or exceeds the defined benchmarks

## Getting Started

To set up the development environment:

1. Initialize the project with `uv init --lib`
2. Install dependencies with `uv sync`
3. Run tests with `uv run pytest`
4. Run a single test with `uv run pytest path/to/test.py::test_function_name`
5. Format code with `uv run ruff format`
6. Lint code with `uv run ruff check .`
7. Type check with `uv run pyright`

To execute sample experimental workflows during development:

```python
import sciflow

# Define an experimental workflow
workflow = sciflow.ExperimentalWorkflow("neural_network_training")

# Define computational tasks
workflow.add_task("preprocess_data", preprocess_function)
workflow.add_task("train_model", train_function, depends_on=["preprocess_data"])
workflow.add_task("evaluate_model", evaluate_function, depends_on=["train_model"])

# Define parameter space
workflow.add_parameter_space({
    "learning_rate": [0.001, 0.01, 0.1],
    "hidden_layers": [1, 2, 3],
    "neurons_per_layer": [64, 128, 256],
    "dropout_rate": [0.1, 0.3, 0.5]
})

# Define resource requirements
workflow.set_resource_requirements({
    "train_model": {
        "cpu_cores": 4,
        "memory_gb": 8,
        "gpu": True,
        "max_runtime_hours": 12
    }
})

# Configure scheduling
workflow.set_scheduling_policy("off_peak", {
    "preferred_hours": "22:00-08:00",
    "weekend_preferred": True,
    "max_wait_hours": 48
})

# Configure result visualization
workflow.add_visualization("accuracy_vs_parameters", {
    "type": "heatmap",
    "x_axis": "learning_rate",
    "y_axis": "hidden_layers",
    "value": "validation_accuracy",
    "facet_by": ["dropout_rate"]
})

# Execute workflow
engine = sciflow.Engine()
results = engine.execute_parameter_sweep(workflow)

# Create reproducibility package
package = sciflow.create_reproducibility_package(
    workflow, 
    results,
    package_name="neural_net_experiment_v1"
)

# Export package
package.export("/path/to/export/directory")

# Analyze results
best_params = results.find_optimal_parameters("validation_accuracy", maximize=True)
print(f"Best parameters: {best_params}")
print(f"Best accuracy: {results.get_metric(best_params, 'validation_accuracy')}")
```