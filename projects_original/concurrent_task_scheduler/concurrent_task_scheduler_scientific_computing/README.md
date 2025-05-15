# Long-Running Simulation Orchestrator

A specialized concurrent task scheduler designed for managing large-scale scientific simulations that run for months across hundreds of compute nodes. This system maximizes research output through efficient scheduling with robust checkpointing, fault tolerance, and scenario prioritization capabilities tailored to long-duration computational science workloads.

## Features

- **Long-Running Job Management System**: Protects extended simulations from preemption while efficiently managing resource allocation over periods of months.
- **Simulation Dependency Tracking**: Tracks relationships between simulation stages and automates transitions between phases of complex models.
- **Equipment Failure Resilience**: Minimizes recalculation after hardware failures with intelligent checkpointing and partial result preservation.
- **Resource Usage Forecasting**: Generates accurate forecasts of simulation resource requirements for grant reporting and capacity planning.
- **Scenario Priority Management**: Adjusts resource allocation among different simulation scenarios based on preliminary result promise and research potential.

## System Architecture

The system is organized into several key components:

1. **Job Management**: Manages long-running simulations with preemption protection and resource scheduling
   - `scheduler.py`: Handles job scheduling and resource allocation
   - `queue.py`: Manages the job queue with prioritization strategies
   - `reservation.py`: Manages resource reservations and conflict resolution

2. **Dependency Tracking**: Manages complex workflows and relationships between simulation stages
   - `graph.py`: Implements a directed graph for tracking dependencies
   - `tracker.py`: Tracks dependencies between simulation components
   - `workflow.py`: Manages multi-stage simulation workflows

3. **Failure Resilience**: Provides robust recovery from hardware failures
   - `checkpoint_manager.py`: Manages creation and restoration of checkpoints
   - `failure_detector.py`: Detects hardware and software failures
   - `resilience_coordinator.py`: Coordinates recovery from failures

4. **Resource Forecasting**: Predicts resource needs for planning
   - `data_collector.py`: Gathers resource utilization data
   - `forecaster.py`: Generates resource usage forecasts
   - `optimizer.py`: Optimizes resource allocation
   - `reporter.py`: Generates reports for resource usage

5. **Scenario Management**: Prioritizes the most promising research directions
   - `comparator.py`: Compares different simulation scenarios
   - `evaluator.py`: Evaluates scenario scientific promise
   - `priority_manager.py`: Adjusts resource allocation based on priorities

## Installation

```bash
# Set up a virtual environment
uv venv
source .venv/bin/activate

# Install the package in development mode
uv pip install -e .

# Install required dependencies
uv pip install networkx scikit-learn pytest pytest-json-report
```

## Usage Examples

```python
# Initialize the job manager
from concurrent_task_scheduler.job_management.scheduler import JobScheduler, LongRunningJobManager

# Create a scheduler with the hybrid strategy
scheduler = JobScheduler()

# Create a long-running job manager
job_manager = LongRunningJobManager(scheduler=scheduler)

# Register compute nodes
from concurrent_task_scheduler.models import ComputeNode, NodeType
node = ComputeNode(
    id="node-1",
    name="Compute Node 1",
    node_type=NodeType.COMPUTE,
    cpu_cores=32,
    memory_gb=128.0,
    gpu_count=4,
    storage_gb=1024.0,
    network_bandwidth_gbps=10.0,
)
job_manager.register_node(node)

# Submit a simulation
from concurrent_task_scheduler.models import Simulation
simulation = Simulation(...)
job_manager.submit_simulation(simulation)
```

## Testing

```bash
# Install the test dependencies
uv pip install pytest pytest-json-report

# Run all tests
pytest

# Generate test coverage report
pytest --cov=concurrent_task_scheduler

# Generate JSON report for validation
pytest --json-report --json-report-file=pytest_results.json
```

## Advanced Features

- **Checkpointing Strategies**: Configure different checkpointing strategies based on simulation type and importance
- **Failure Recovery**: Automatically recover from various failure scenarios with minimal data loss
- **Dynamic Priority Adjustment**: Adjust simulation priorities based on preliminary results and system conditions
- **Resource Forecasting**: Generate accurate forecasts for future resource needs based on historical patterns
- **Maintenance Windows**: Handle planned system maintenance with minimal disruption to long-running simulations