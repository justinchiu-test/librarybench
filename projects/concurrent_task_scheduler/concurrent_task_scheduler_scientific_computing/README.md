# Long-Running Simulation Orchestrator

A specialized concurrent task scheduler designed for managing large-scale scientific simulations that run for months across hundreds of compute nodes. This system maximizes research output through efficient scheduling with robust checkpointing, fault tolerance, and scenario prioritization capabilities tailored to long-duration computational science workloads.

## Features

- **Long-Running Job Management System**: Protects extended simulations from preemption while efficiently managing resource allocation.
- **Simulation Dependency Tracking**: Tracks relationships between simulation stages and automates transitions between phases.
- **Equipment Failure Resilience**: Minimizes recalculation after hardware failures with intelligent checkpointing.
- **Resource Usage Forecasting**: Generates accurate forecasts of simulation resource requirements.
- **Scenario Priority Management**: Adjusts resource allocation based on preliminary result promise.

## Installation

```bash
# Set up a virtual environment
uv venv
source .venv/bin/activate

# Install the package in development mode
uv pip install -e .
```

## Testing

```bash
# Run all tests
pytest

# Generate test coverage report
pytest --cov=concurrent_task_scheduler

# Generate JSON report for validation
pytest --json-report --json-report-file=pytest_results.json
```