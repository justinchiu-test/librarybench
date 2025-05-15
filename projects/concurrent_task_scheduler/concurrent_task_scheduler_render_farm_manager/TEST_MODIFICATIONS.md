# Model Compatibility Modifications

This document outlines the changes needed to make the test files compatible with the actual model implementations in the codebase.

## Key Class Differences

### 1. Client vs RenderClient
- **Actual implementation**: `Client` class
  - ID field: `id` (string)
  - Service tier: `sla_tier` (string)
  - Added fields: `guaranteed_resources`, `max_resources`
- **Test assumption**: `RenderClient` class
  - ID field: `client_id` (string)
  - Service tier: `service_tier` (ServiceTier enum)

### 2. RenderNode Structure
- **Actual implementation**: Uses `NodeCapabilities` object for specs
  - Node identifiers: `id`, `name`
  - Capabilities contained in `capabilities` object
  - Specialized capabilities in `capabilities.specialized_for` list
- **Test assumption**: Direct attributes on RenderNode
  - Node identifiers: `node_id`, `name`
  - Direct attributes like `cpu_cores`, `memory_gb`
  - Node type specified using `node_type` (NodeType enum)

### 3. RenderJob Structure
- **Actual implementation**:
  - ID field: `id` (string)
  - Status: `status` (RenderJobStatus enum)
  - Priority: `priority` (JobPriority enum)
  - Memory: `memory_requirements_gb` (int)
  - GPU: `requires_gpu` (boolean)
- **Test assumption**:
  - ID field: `job_id` (string)
  - Priority: numeric value (e.g., 100, 50)
  - Memory: `memory_requirements` (int)
  - GPU: `gpu_requirements` (int)

## Required Test Modifications

### 1. Replace RenderClient with Client
```python
# FROM
client = RenderClient(
    client_id="premium", 
    name="Premium Client", 
    service_tier=ServiceTier.PREMIUM
)

# TO
client = Client(
    id="premium", 
    name="Premium Client", 
    sla_tier="premium",
    guaranteed_resources=50,
    max_resources=80
)
```

### 2. Update RenderNode Structure
```python
# FROM
node = RenderNode(
    node_id="node1",
    name="Node 1",
    node_type=NodeType.GPU,
    cpu_cores=16,
    memory_gb=64,
    gpu_count=2
)

# TO
node = RenderNode(
    id="node1",
    name="Node 1",
    status="online",
    capabilities=NodeCapabilities(
        cpu_cores=16,
        memory_gb=64,
        gpu_model="NVIDIA RTX A6000",
        gpu_count=2,
        gpu_memory_gb=24,
        gpu_compute_capability=8.6,
        storage_gb=2000,
        specialized_for=["gpu_rendering"]
    ),
    power_efficiency_rating=85,
    current_job_id=None,
    performance_history={},
    last_error=None,
    uptime_hours=100
)
```

### 3. Update RenderJob Structure
```python
# FROM
job = RenderJob(
    job_id="job1",
    client_id="client1",
    name="Job 1",
    priority=100,
    cpu_requirements=8,
    memory_requirements=32,
    gpu_requirements=2,
    estimated_duration_hours=4.0,
    deadline=deadline_time
)

# TO
job = RenderJob(
    id="job1",
    name="Job 1",
    client_id="client1",
    status=RenderJobStatus.PENDING,
    job_type="animation",
    priority=JobPriority.HIGH,
    submission_time=submission_time,
    deadline=deadline_time,
    estimated_duration_hours=4.0,
    progress=0.0,
    requires_gpu=True,
    memory_requirements_gb=32,
    cpu_requirements=8,
    scene_complexity=7,
    dependencies=[],
    assigned_node_id=None,
    output_path="/renders/job1/",
    error_count=0
)
```

### 4. Fix Test Assertions
Update test assertions that reference the old attribute names:

```python
# FROM
assert node.gpu_count >= 2

# TO
assert node.capabilities.gpu_count >= 2
```

### 5. Replace Enum Values
```python
# FROM
priority=100  # High priority as numeric value

# TO
priority=JobPriority.HIGH  # Using enum
```

## Implementation Example

Two test files have been updated with these changes:
1. `/tests/unit/test_resource_borrowing_fixed.py`
2. `/tests/integration/test_energy_modes_fixed.py`

These files can be used as a reference for updating the remaining test files.