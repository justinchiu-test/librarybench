# Render Farm Manager

A comprehensive system for managing and optimizing 3D rendering tasks across distributed computing resources.

## Overview

The Render Farm Manager is a powerful system designed for orchestrating rendering jobs across multiple nodes in a 3D rendering farm. It handles job scheduling, resource allocation, performance optimization, and more to ensure efficient utilization of rendering resources while meeting client requirements and deadlines.

## Key Features

- **Deadline-driven Scheduling**: Intelligent job scheduling based on priorities and deadlines
- **Client Resource Partitioning**: Fair resource allocation based on client SLAs
- **Node Specialization**: Matching jobs to the most suitable render nodes
- **Progressive Result Generation**: Create intermediate outputs during long-running renders
- **Energy Optimization**: Reduce power consumption while maintaining performance
- **Fault Tolerance**: Handle node failures and automatically reschedule affected jobs
- **Performance Monitoring**: Track system utilization and efficiency metrics
- **Comprehensive Audit Logging**: Detailed history of all system events

## Architecture

The system is built with a modular architecture where each component handles a specific aspect of render farm management:

### Core Components

- **RenderFarmManager**: Central component that integrates all functionality
- **DeadlineScheduler**: Manages job priorities and scheduling decisions
- **ResourcePartitioner**: Allocates resources between clients based on SLAs
- **NodeSpecializationManager**: Matches jobs to nodes based on capabilities
- **ProgressiveRenderer**: Generates intermediate results for long-running jobs
- **EnergyOptimizer**: Optimizes node usage for energy efficiency
- **AuditLogger**: Records detailed system activity
- **PerformanceMonitor**: Tracks system performance metrics

### Data Models

Key data models include:

- **RenderJob**: Represents a rendering task with requirements and status
- **RenderNode**: Represents a computing node with capabilities
- **Client**: Represents a client organization with SLA details
- **ResourceAllocation**: Tracks resource allocation between clients
- **PerformanceMetrics**: Stores performance statistics

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/render-farm-manager.git
cd render-farm-manager

# Install the package
pip install -e .
```

## Usage Examples

### Basic Initialization

```python
from render_farm_manager.core.manager import RenderFarmManager

# Initialize with default components
manager = RenderFarmManager()
```

### Custom Initialization

```python
from render_farm_manager.core.manager import RenderFarmManager
from render_farm_manager.scheduling.deadline_scheduler import DeadlineScheduler
from render_farm_manager.resource_management.resource_partitioner import ResourcePartitioner
from render_farm_manager.utils.logging import AuditLogger, PerformanceMonitor

# Initialize components
audit_logger = AuditLogger()
performance_monitor = PerformanceMonitor(audit_logger)

# Configure custom components
scheduler = DeadlineScheduler(
    audit_logger=audit_logger,
    performance_monitor=performance_monitor,
    deadline_safety_margin_hours=2.0,
    enable_preemption=True
)

resource_manager = ResourcePartitioner(
    audit_logger=audit_logger,
    performance_monitor=performance_monitor,
    allow_borrowing=True,
    borrowing_limit_percentage=50.0
)

# Initialize manager with custom components
manager = RenderFarmManager(
    scheduler=scheduler,
    resource_manager=resource_manager,
    audit_logger=audit_logger,
    performance_monitor=performance_monitor
)
```

### Adding Resources and Submitting Jobs

```python
from datetime import datetime, timedelta
from render_farm_manager.core.models import Client, RenderNode, NodeCapabilities, RenderJob, JobPriority, RenderJobStatus

# Add a client
client = Client(
    id="client1",
    name="VFX Studio",
    sla_tier="premium",
    guaranteed_resources=30,
    max_resources=50
)
manager.add_client(client)

# Add a render node
node = RenderNode(
    id="node1",
    name="RenderBox-01",
    status="online",
    capabilities=NodeCapabilities(
        cpu_cores=32,
        memory_gb=128,
        gpu_model="RTX 4090",
        gpu_count=4,
        gpu_memory_gb=24,
        gpu_compute_capability=8.9,
        storage_gb=2000,
        specialized_for=["fluid-simulation", "path-tracing"]
    ),
    power_efficiency_rating=85.0
)
manager.add_node(node)

# Submit a job
job = RenderJob(
    id="job1",
    name="Ocean Scene Final Render",
    client_id="client1",
    status=RenderJobStatus.PENDING,
    job_type="feature-film",
    priority=JobPriority.HIGH,
    submission_time=datetime.now(),
    deadline=datetime.now() + timedelta(days=2),
    estimated_duration_hours=12.0,
    requires_gpu=True,
    memory_requirements_gb=64,
    cpu_requirements=16,
    scene_complexity=8,
    output_path="/renders/client1/ocean_scene_final/",
    supports_progressive_output=True,
    supports_checkpoint=True,
    energy_intensive=True
)
manager.submit_job(job)

# Run scheduling cycle to assign jobs to nodes
results = manager.run_scheduling_cycle()
print(f"Jobs scheduled: {results['jobs_scheduled']}")
print(f"Farm utilization: {results['utilization_percentage']:.1f}%")
```

### Monitoring System Status

```python
# Get overall farm status
farm_status = manager.get_farm_status()
print(f"Total nodes: {farm_status['total_nodes']}")
print(f"Online nodes: {farm_status['nodes_by_status'].get('online', 0)}")
print(f"Active jobs: {farm_status['jobs_by_status'].get('running', 0)}")

# Get client status
client_status = manager.get_client_status("client1")
print(f"Client resource usage: {client_status['current_resource_usage']:.1f}%")
print(f"Active jobs: {len(client_status['active_jobs'])}")

# Get job status
job_status = manager.get_job_status("job1")
print(f"Job status: {job_status['status']}")
print(f"Progress: {job_status['progress']:.1f}%")
print(f"Will meet deadline: {job_status['will_meet_deadline']}")
```

## Project Structure

```
render_farm_manager/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── interfaces.py     # Abstract interfaces for all components
│   ├── manager.py        # Main RenderFarmManager class
│   └── models.py         # Data models and types
├── energy_optimization/
│   ├── __init__.py
│   └── energy_optimizer.py
├── node_specialization/
│   ├── __init__.py
│   └── specialization_manager.py
├── progressive_result/
│   ├── __init__.py
│   └── progressive_renderer.py
├── resource_management/
│   ├── __init__.py
│   └── resource_partitioner.py
├── scheduling/
│   ├── __init__.py
│   └── deadline_scheduler.py
└── utils/
    ├── __init__.py
    └── logging.py        # Audit logging and performance monitoring
```

## Core Data Models

### RenderJob

Represents a rendering task with all its requirements and status:

- `id`: Unique identifier
- `name`: Human-readable name
- `client_id`: ID of the client that submitted the job
- `status`: Current job status (pending, running, completed, etc.)
- `priority`: Job priority level
- `deadline`: When the job must be completed
- `estimated_duration_hours`: Expected rendering time
- `requires_gpu`: Whether the job requires GPU for rendering
- `memory_requirements_gb`: Required memory in GB
- `cpu_requirements`: Required CPU cores
- `scene_complexity`: Complexity rating (1-10)
- `dependencies`: List of job IDs that must complete before this job
- `assigned_node_id`: ID of the node assigned to render this job
- `supports_progressive_output`: Whether progressive output is enabled
- `supports_checkpoint`: Whether checkpointing is enabled

### RenderNode

Represents a computing node in the render farm:

- `id`: Unique identifier
- `name`: Human-readable name
- `status`: Current node status (online, offline, error, etc.)
- `capabilities`: Detailed specs including CPU, GPU, memory
- `power_efficiency_rating`: Energy efficiency rating
- `current_job_id`: ID of the job currently running on this node
- `performance_history`: Historical performance metrics
- `uptime_hours`: How long the node has been running

### Client

Represents a client organization:

- `id`: Unique identifier
- `name`: Organization name
- `sla_tier`: Service level agreement tier
- `guaranteed_resources`: Minimum resource percentage guaranteed
- `max_resources`: Maximum percentage of resources allowed

## Test Cases

The system includes comprehensive test coverage:

1. **Fault Tolerance**
   - `test_fault_tolerance.py`: Tests system resilience to multiple simultaneous node failures
   - Verifies jobs are properly rescheduled when nodes fail
   - Checks that node failure tracking is properly performed

2. **Resource Borrowing**
   - `test_resource_borrowing.py`: Tests client resource borrowing capabilities
   - Verifies resource sharing between clients with different demand
   - Tests different borrowing limit percentages and their effects

3. **Error Recovery**
   - `test_error_recovery.py`: Tests job recovery via checkpoints after failures
   - Verifies behavior with multiple sequential failures
   - Tests error count threshold handling

4. **Energy Modes**
   - `test_energy_modes.py`: Tests dynamic switching between energy modes
   - Verifies night savings mode functionality for energy-intensive jobs
   - Validates power efficiency considerations in scheduling

5. **Job Dependencies**
   - `test_job_dependencies.py`: Tests proper handling of job dependency chains
   - Verifies child jobs only run after parent jobs complete
   - Tests priority inheritance for dependent jobs
   - Handles circular dependency detection

6. **Audit Logging**
   - `test_audit_logging.py`: Tests comprehensive logging of system operations
   - Verifies proper log level handling
   - Tests performance metrics tracking alongside audit logs

## Implementation Notes

Due to API differences between the test assumptions and actual implementation, test files need to be modified to match the actual model implementations:

1. Replace `RenderClient` with `Client`
2. Use `NodeCapabilities` for node specifications
3. Use `id` instead of `client_id`, `node_id`, etc.
4. Use string literals ("premium", "standard", "basic") instead of enum values
5. Fix manager initialization to use `performance_monitor` instead of `performance_metrics`
6. Add required error parameter to `handle_node_failure` calls

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.