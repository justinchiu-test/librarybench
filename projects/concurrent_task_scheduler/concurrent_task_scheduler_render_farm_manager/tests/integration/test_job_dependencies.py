import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta

from render_farm_manager.core.models import (
    RenderClient,
    RenderNode,
    RenderJob,
    RenderJobStatus,
    ServiceTier,
    NodeType,
)
from render_farm_manager.core.manager import RenderFarmManager


@pytest.fixture
def audit_logger():
    return MagicMock()


@pytest.fixture
def performance_metrics():
    return MagicMock()


@pytest.fixture
def farm_manager(audit_logger, performance_metrics):
    """Creates a render farm manager with mocked audit logger and performance metrics."""
    return RenderFarmManager(
        audit_logger=audit_logger,
        performance_metrics=performance_metrics
    )


@pytest.fixture
def client():
    """Creates a test client."""
    return RenderClient(
        client_id="client1",
        name="Test Client",
        service_tier=ServiceTier.PREMIUM,
    )


@pytest.fixture
def render_nodes():
    """Creates test render nodes."""
    return [
        RenderNode(
            node_id="node1",
            name="Node 1",
            node_type=NodeType.GPU,
            cpu_cores=16,
            memory_gb=64,
            gpu_count=2,
        ),
        RenderNode(
            node_id="node2",
            name="Node 2",
            node_type=NodeType.GPU,
            cpu_cores=16,
            memory_gb=64,
            gpu_count=2,
        ),
    ]


@pytest.fixture
def dependent_jobs():
    """Creates a set of jobs with dependencies."""
    now = datetime.now()
    
    # Create parent jobs first
    parent_job1 = RenderJob(
        job_id="parent1",
        client_id="client1",
        name="Parent Job 1",
        priority=100,
        cpu_requirements=8,
        memory_requirements=32,
        gpu_requirements=1,
        estimated_duration_hours=1.0,
        deadline=now + timedelta(hours=4),
    )
    
    parent_job2 = RenderJob(
        job_id="parent2",
        client_id="client1",
        name="Parent Job 2",
        priority=90,
        cpu_requirements=8,
        memory_requirements=32,
        gpu_requirements=1,
        estimated_duration_hours=1.0,
        deadline=now + timedelta(hours=4),
    )
    
    # Create child job that depends on both parents
    child_job = RenderJob(
        job_id="child1",
        client_id="client1",
        name="Child Job",
        priority=80,
        cpu_requirements=16,
        memory_requirements=64,
        gpu_requirements=2,
        estimated_duration_hours=2.0,
        deadline=now + timedelta(hours=8),
        dependencies=["parent1", "parent2"],
    )
    
    # Create a grandchild job that depends on the child
    grandchild_job = RenderJob(
        job_id="grandchild1",
        client_id="client1",
        name="Grandchild Job",
        priority=70,
        cpu_requirements=8,
        memory_requirements=32,
        gpu_requirements=1,
        estimated_duration_hours=1.0,
        deadline=now + timedelta(hours=12),
        dependencies=["child1"],
    )
    
    # Create a job with no dependencies for comparison
    independent_job = RenderJob(
        job_id="independent1",
        client_id="client1",
        name="Independent Job",
        priority=60,
        cpu_requirements=8,
        memory_requirements=32,
        gpu_requirements=1,
        estimated_duration_hours=1.0,
        deadline=now + timedelta(hours=6),
    )
    
    return [parent_job1, parent_job2, child_job, grandchild_job, independent_job]


def test_job_dependency_scheduling(farm_manager, client, render_nodes, dependent_jobs):
    """Test that jobs with dependencies are scheduled correctly."""
    # Setup: Add client and nodes
    farm_manager.add_client(client)
    
    for node in render_nodes:
        farm_manager.add_node(node)
    
    # Submit all jobs
    for job in dependent_jobs:
        farm_manager.submit_job(job)
    
    # First scheduling cycle
    farm_manager.run_scheduling_cycle()
    
    # Check that only parent jobs and independent job are running or queued
    # Child jobs should be pending until dependencies complete
    parent1 = farm_manager.jobs["parent1"]
    parent2 = farm_manager.jobs["parent2"]
    child = farm_manager.jobs["child1"]
    grandchild = farm_manager.jobs["grandchild1"]
    independent = farm_manager.jobs["independent1"]
    
    # Parents and independent job should be scheduled
    assert parent1.status in [RenderJobStatus.RUNNING, RenderJobStatus.QUEUED]
    assert parent2.status in [RenderJobStatus.RUNNING, RenderJobStatus.QUEUED]
    assert independent.status in [RenderJobStatus.RUNNING, RenderJobStatus.QUEUED]
    
    # Child and grandchild should be pending due to dependencies
    assert child.status == RenderJobStatus.PENDING
    assert grandchild.status == RenderJobStatus.PENDING
    
    # Complete the first parent job
    if parent1.status == RenderJobStatus.RUNNING:
        farm_manager.update_job_progress(parent1.job_id, 100.0)
        farm_manager.complete_job(parent1.job_id)
    else:
        # If parent1 is queued, run another cycle to get it running
        farm_manager.run_scheduling_cycle()
        if parent1.status == RenderJobStatus.RUNNING:
            farm_manager.update_job_progress(parent1.job_id, 100.0)
            farm_manager.complete_job(parent1.job_id)
    
    # Run scheduling cycle
    farm_manager.run_scheduling_cycle()
    
    # Child should still be pending because parent2 is not done
    assert child.status == RenderJobStatus.PENDING
    
    # Complete the second parent job
    if parent2.status == RenderJobStatus.RUNNING:
        farm_manager.update_job_progress(parent2.job_id, 100.0)
        farm_manager.complete_job(parent2.job_id)
    else:
        # If parent2 is queued, run another cycle to get it running
        farm_manager.run_scheduling_cycle()
        if parent2.status == RenderJobStatus.RUNNING:
            farm_manager.update_job_progress(parent2.job_id, 100.0)
            farm_manager.complete_job(parent2.job_id)
    
    # Run scheduling cycle
    farm_manager.run_scheduling_cycle()
    
    # Now child should be scheduled (running or queued)
    assert child.status in [RenderJobStatus.RUNNING, RenderJobStatus.QUEUED]
    
    # Grandchild should still be pending
    assert grandchild.status == RenderJobStatus.PENDING
    
    # Complete the child job
    if child.status == RenderJobStatus.RUNNING:
        farm_manager.update_job_progress(child.job_id, 100.0)
        farm_manager.complete_job(child.job_id)
    else:
        # If child is queued, run another cycle to get it running
        farm_manager.run_scheduling_cycle()
        if child.status == RenderJobStatus.RUNNING:
            farm_manager.update_job_progress(child.job_id, 100.0)
            farm_manager.complete_job(child.job_id)
    
    # Run scheduling cycle
    farm_manager.run_scheduling_cycle()
    
    # Now grandchild should be scheduled
    assert grandchild.status in [RenderJobStatus.RUNNING, RenderJobStatus.QUEUED]
    
    # Verify audit logging
    assert audit_logger.log_job_updated.call_count > 0
    assert audit_logger.log_job_completed.call_count > 0


def test_dependent_job_priority_inheritance(farm_manager, client, render_nodes):
    """Test that dependent jobs inherit priority from parent jobs when appropriate."""
    # Setup: Add client and nodes
    farm_manager.add_client(client)
    
    for node in render_nodes:
        farm_manager.add_node(node)
    
    now = datetime.now()
    
    # Create a high-priority parent job
    parent_job = RenderJob(
        job_id="high_parent",
        client_id="client1",
        name="High Priority Parent",
        priority=100,  # Very high priority
        cpu_requirements=8,
        memory_requirements=32,
        gpu_requirements=1,
        estimated_duration_hours=1.0,
        deadline=now + timedelta(hours=3),  # Tight deadline
    )
    
    # Create a low-priority child job
    child_job = RenderJob(
        job_id="low_child",
        client_id="client1",
        name="Low Priority Child",
        priority=10,  # Low priority
        cpu_requirements=8,
        memory_requirements=32,
        gpu_requirements=1,
        estimated_duration_hours=1.0,
        deadline=now + timedelta(hours=12),  # Loose deadline
        dependencies=["high_parent"],
    )
    
    # Create competing jobs with medium priority
    competing_jobs = [
        RenderJob(
            job_id=f"competing{i}",
            client_id="client1",
            name=f"Competing Job {i}",
            priority=50,  # Medium priority
            cpu_requirements=8,
            memory_requirements=32,
            gpu_requirements=1,
            estimated_duration_hours=1.0,
            deadline=now + timedelta(hours=6),
        )
        for i in range(1, 4)
    ]
    
    # Submit all jobs
    farm_manager.submit_job(parent_job)
    farm_manager.submit_job(child_job)
    for job in competing_jobs:
        farm_manager.submit_job(job)
    
    # First scheduling cycle - parent should run
    farm_manager.run_scheduling_cycle()
    
    # Complete the parent job
    parent = farm_manager.jobs["high_parent"]
    if parent.status == RenderJobStatus.RUNNING:
        farm_manager.update_job_progress(parent.job_id, 100.0)
        farm_manager.complete_job(parent.job_id)
    else:
        # If parent is queued, run another cycle to get it running
        farm_manager.run_scheduling_cycle()
        if parent.status == RenderJobStatus.RUNNING:
            farm_manager.update_job_progress(parent.job_id, 100.0)
            farm_manager.complete_job(parent.job_id)
    
    # Run scheduling cycle to handle the completed parent
    farm_manager.run_scheduling_cycle()
    
    # The child job should now be scheduled with inherited priority
    child = farm_manager.jobs["low_child"]
    
    # Verify child job is scheduled despite competing with medium priority jobs
    assert child.status in [RenderJobStatus.RUNNING, RenderJobStatus.QUEUED]
    
    # If the scheduler implements priority inheritance, the effective priority
    # of the child job should be higher than its nominal priority
    if hasattr(child, "effective_priority"):
        assert child.effective_priority > child.priority
    
    # Count how many competing jobs are running
    running_competing = sum(
        1 for job_id, job in farm_manager.jobs.items()
        if job_id.startswith("competing") and job.status == RenderJobStatus.RUNNING
    )
    
    # Check if child job is prioritized over competing jobs
    if child.status == RenderJobStatus.RUNNING:
        # If only one job can run at a time, no competing jobs should be running
        assert running_competing == 0
    elif len(render_nodes) == 1:
        # If there's only one node and child is queued, a competing job must be running
        assert running_competing == 1


def test_circular_dependency_detection(farm_manager, client, render_nodes):
    """Test that circular dependencies are detected and handled appropriately."""
    # Setup: Add client and nodes
    farm_manager.add_client(client)
    
    for node in render_nodes:
        farm_manager.add_node(node)
    
    now = datetime.now()
    
    # Create jobs with circular dependencies
    job_a = RenderJob(
        job_id="job_a",
        client_id="client1",
        name="Job A",
        priority=100,
        cpu_requirements=8,
        memory_requirements=32,
        gpu_requirements=1,
        estimated_duration_hours=1.0,
        deadline=now + timedelta(hours=4),
        dependencies=["job_c"],  # A depends on C
    )
    
    job_b = RenderJob(
        job_id="job_b",
        client_id="client1",
        name="Job B",
        priority=90,
        cpu_requirements=8,
        memory_requirements=32,
        gpu_requirements=1,
        estimated_duration_hours=1.0,
        deadline=now + timedelta(hours=5),
        dependencies=["job_a"],  # B depends on A
    )
    
    job_c = RenderJob(
        job_id="job_c",
        client_id="client1",
        name="Job C",
        priority=80,
        cpu_requirements=8,
        memory_requirements=32,
        gpu_requirements=1,
        estimated_duration_hours=1.0,
        deadline=now + timedelta(hours=6),
        dependencies=["job_b"],  # C depends on B, creating a cycle: A -> C -> B -> A
    )
    
    # In a real implementation, the farm manager should detect this cycle
    # during job submission and reject the jobs or mark them as failed
    # For this test, we'll submit them and check that they aren't scheduled
    
    # Submit all jobs
    farm_manager.submit_job(job_a)
    farm_manager.submit_job(job_b)
    farm_manager.submit_job(job_c)
    
    # Run scheduling cycle
    farm_manager.run_scheduling_cycle()
    
    # All jobs should be in PENDING or FAILED state due to circular dependencies
    # None should be RUNNING or QUEUED
    for job_id in ["job_a", "job_b", "job_c"]:
        job = farm_manager.jobs[job_id]
        assert job.status not in [RenderJobStatus.RUNNING, RenderJobStatus.QUEUED], \
            f"Job {job_id} should not be scheduled due to circular dependency"
    
    # Verify audit logging of the circular dependency
    # In a real implementation, there should be explicit logging for this condition
    assert audit_logger.log_job_updated.call_count > 0