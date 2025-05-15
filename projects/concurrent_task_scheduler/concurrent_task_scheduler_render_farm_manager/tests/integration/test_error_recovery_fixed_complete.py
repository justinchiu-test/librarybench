"""Comprehensive fixed integration tests for error recovery functionality."""

import pytest
from datetime import datetime, timedelta

from render_farm_manager.core.models import (
    Client,
    RenderNode,
    RenderJob,
    RenderJobStatus,
    NodeCapabilities,
    JobPriority,
)
from render_farm_manager.core.manager import RenderFarmManager


def test_error_recovery_with_checkpoint():
    """Test that jobs can properly recover from node failures using checkpoints."""
    # Create a fresh render farm manager
    farm_manager = RenderFarmManager()
    
    # Add a client
    client = Client(
        id="client1",
        name="Test Client",
        sla_tier="premium",
        guaranteed_resources=50,
        max_resources=80,
    )
    farm_manager.add_client(client)
    
    # Add two nodes
    node1 = RenderNode(
        id="node1",
        name="Node 1",
        status="online",
        capabilities=NodeCapabilities(
            cpu_cores=16,
            memory_gb=64,
            gpu_model="NVIDIA RTX A6000",
            gpu_count=2,
            gpu_memory_gb=48.0,
            gpu_compute_capability=8.6,
            storage_gb=512,
            specialized_for=["gpu_rendering"],
        ),
        power_efficiency_rating=75.0,
    )
    
    node2 = RenderNode(
        id="node2",
        name="Node 2",
        status="online",
        capabilities=NodeCapabilities(
            cpu_cores=16,
            memory_gb=64,
            gpu_model="NVIDIA RTX A6000",
            gpu_count=2,
            gpu_memory_gb=48.0,
            gpu_compute_capability=8.6,
            storage_gb=512,
            specialized_for=["gpu_rendering"],
        ),
        power_efficiency_rating=75.0,
    )
    
    farm_manager.add_node(node1)
    farm_manager.add_node(node2)
    
    # Create a job that supports checkpoints
    now = datetime.now()
    job = RenderJob(
        id="job1",
        client_id="client1",
        name="Checkpoint Job",
        status=RenderJobStatus.PENDING,
        job_type="animation",
        priority=JobPriority.HIGH,
        submission_time=now,
        deadline=now + timedelta(hours=5),
        estimated_duration_hours=2.0,
        progress=0.0,
        requires_gpu=True,
        memory_requirements_gb=32,
        cpu_requirements=8,
        scene_complexity=6,
        dependencies=[],
        output_path="/renders/client1/job1/",
        supports_checkpoint=True,
    )
    
    # Submit the job
    farm_manager.submit_job(job)
    
    # First scheduling cycle
    farm_manager.run_scheduling_cycle()
    job = farm_manager.jobs["job1"]
    
    # Verify job is running
    assert job.status == RenderJobStatus.RUNNING
    assert job.assigned_node_id is not None
    original_node_id = job.assigned_node_id
    
    # Update progress to 50% and set a checkpoint
    farm_manager.update_job_progress("job1", 50.0)
    checkpoint_time = datetime.now()
    job.last_checkpoint_time = checkpoint_time
    
    # Simulate node failure
    farm_manager.handle_node_failure(original_node_id, "Hardware failure")
    
    # Verify job state after failure
    assert job.status == RenderJobStatus.QUEUED
    assert job.assigned_node_id is None
    assert job.error_count == 1
    assert job.progress == 50.0  # Progress should be preserved
    assert job.last_checkpoint_time == checkpoint_time
    
    # Run another scheduling cycle
    farm_manager.run_scheduling_cycle()
    
    # Verify job is running again
    assert job.status == RenderJobStatus.RUNNING
    assert job.assigned_node_id is not None
    assert job.assigned_node_id != original_node_id  # Should be assigned to a different node
    
    # Complete the job
    farm_manager.update_job_progress("job1", 100.0)
    farm_manager.complete_job("job1")
    
    # Verify job completion
    assert job.status == RenderJobStatus.COMPLETED


def test_error_count_threshold_handling():
    """Test that jobs exceeding error threshold are handled correctly."""
    # Create a fresh render farm manager
    farm_manager = RenderFarmManager()
    
    # Add a client
    client = Client(
        id="client1",
        name="Test Client",
        sla_tier="premium",
        guaranteed_resources=50,
        max_resources=80,
    )
    farm_manager.add_client(client)
    
    # Add a node
    node = RenderNode(
        id="node1",
        name="Node 1",
        status="online",
        capabilities=NodeCapabilities(
            cpu_cores=16,
            memory_gb=64,
            gpu_model="NVIDIA RTX A6000",
            gpu_count=2,
            gpu_memory_gb=48.0,
            gpu_compute_capability=8.6,
            storage_gb=512,
            specialized_for=["gpu_rendering"],
        ),
        power_efficiency_rating=75.0,
    )
    farm_manager.add_node(node)
    
    # Create a job
    now = datetime.now()
    job = RenderJob(
        id="job1",
        client_id="client1",
        name="Unstable Job",
        status=RenderJobStatus.PENDING,
        job_type="animation",
        priority=JobPriority.HIGH,
        submission_time=now,
        deadline=now + timedelta(hours=5),
        estimated_duration_hours=2.0,
        progress=0.0,
        requires_gpu=True,
        memory_requirements_gb=32,
        cpu_requirements=8,
        scene_complexity=6,
        dependencies=[],
        output_path="/renders/client1/job1/",
        supports_checkpoint=True,
    )
    
    # Submit the job
    farm_manager.submit_job(job)
    
    # Manually set the error count to 3 (threshold)
    job = farm_manager.jobs["job1"]
    job.error_count = 3
    
    # Simulate a node failure that should trigger the threshold
    farm_manager.run_scheduling_cycle()
    assert job.status == RenderJobStatus.RUNNING
    farm_manager.handle_node_failure(job.assigned_node_id, "Hardware failure")
    
    # Job should now be failed due to exceeding error threshold
    assert job.status == RenderJobStatus.FAILED
    assert job.error_count == 4  # Should be incremented one last time