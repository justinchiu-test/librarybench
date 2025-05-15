import pytest
from unittest.mock import MagicMock
from datetime import datetime, timedelta

from render_farm_manager.core.models import (
    RenderClient,
    RenderNode,
    RenderJob,
    ResourceAllocation,
    ServiceTier,
    NodeType,
    NodeCapabilities,
    JobPriority,
    NodeStatus,
)
from render_farm_manager.resource_management.resource_partitioner import ResourcePartitioner


@pytest.fixture
def audit_logger():
    """Creates a mock audit logger with all necessary methods."""
    mock = MagicMock()
    # Add specific methods that might be called during testing
    mock.log_client_added = MagicMock()
    mock.log_resource_allocation = MagicMock()
    return mock


@pytest.fixture
def performance_monitor():
    """Creates a mock performance monitor with all necessary methods."""
    mock = MagicMock()
    # Add specific methods that might be called during testing
    mock.update_client_resource_metrics = MagicMock()
    return mock


@pytest.fixture
def clients():
    """Creates test clients with different service tiers."""
    return [
        RenderClient(
            client_id="premium", 
            name="Premium Client", 
            service_tier=ServiceTier.PREMIUM,
            guaranteed_resources=50,
            max_resources=80
        ),
        RenderClient(
            client_id="standard", 
            name="Standard Client", 
            service_tier=ServiceTier.STANDARD,
            guaranteed_resources=30,
            max_resources=60
        ),
        RenderClient(
            client_id="basic", 
            name="Basic Client", 
            service_tier=ServiceTier.BASIC,
            guaranteed_resources=10,
            max_resources=40
        ),
    ]


@pytest.fixture
def render_nodes():
    """Creates test render nodes of different types."""
    return [
        RenderNode(
            id=f"node{i}",
            name=f"Node {i}",
            status=NodeStatus.ONLINE,
            capabilities=NodeCapabilities(
                cpu_cores=16,
                memory_gb=64,
                gpu_model="NVIDIA RTX A6000" if i % 3 == 0 else None,
                gpu_count=2 if i % 3 == 0 else 0,
                gpu_memory_gb=48.0 if i % 3 == 0 else 0.0,
                gpu_compute_capability=8.6 if i % 3 == 0 else 0.0,
                storage_gb=512 if i % 3 != 2 else 1024,
                specialized_for=["rendering", "compositing"] if i % 3 == 0 else 
                              (["simulation", "procedural"] if i % 3 == 1 else ["simulation", "fluid"])
            ),
            power_efficiency_rating=75.0 if i % 3 == 0 else (85.0 if i % 3 == 1 else 80.0),
        )
        for i in range(1, 11)  # 10 nodes total
    ]


@pytest.fixture
def render_jobs():
    """Creates test render jobs with varying resource requirements."""
    now = datetime.now()
    return [
        # Premium client jobs - high demand
        RenderJob(
            id="premium_job1",
            client_id="premium",
            name="Premium Job 1",
            status=RenderJobStatus.PENDING,
            job_type="animation",
            priority=JobPriority.HIGH,
            submission_time=now,
            deadline=now + timedelta(hours=4),
            estimated_duration_hours=2.0,
            progress=0.0,
            requires_gpu=True,
            memory_requirements_gb=32,
            cpu_requirements=8,
            scene_complexity=7,
            output_path="/renders/premium/job1/",
        ),
        RenderJob(
            id="premium_job2",
            client_id="premium",
            name="Premium Job 2",
            status=RenderJobStatus.PENDING,
            job_type="vfx",
            priority=JobPriority.HIGH,
            submission_time=now,
            deadline=now + timedelta(hours=6),
            estimated_duration_hours=1.0,
            progress=0.0,
            requires_gpu=True,
            memory_requirements_gb=32,
            cpu_requirements=8,
            scene_complexity=6,
            output_path="/renders/premium/job2/",
        ),
        
        # Standard client jobs - medium demand
        RenderJob(
            id="standard_job1",
            client_id="standard",
            name="Standard Job 1",
            status=RenderJobStatus.PENDING,
            job_type="lighting",
            priority=JobPriority.MEDIUM,
            submission_time=now,
            deadline=now + timedelta(hours=8),
            estimated_duration_hours=3.0,
            progress=0.0,
            requires_gpu=False,
            memory_requirements_gb=32,
            cpu_requirements=8,
            scene_complexity=5,
            output_path="/renders/standard/job1/",
        ),
        
        # Basic client jobs - low demand initially, then increases
        RenderJob(
            id="basic_job1",
            client_id="basic",
            name="Basic Job 1",
            status=RenderJobStatus.PENDING,
            job_type="simulation",
            priority=JobPriority.LOW,
            submission_time=now,
            deadline=now + timedelta(hours=12),
            estimated_duration_hours=1.0,
            progress=0.0,
            requires_gpu=False,
            memory_requirements_gb=16,
            cpu_requirements=4,
            scene_complexity=4,
            output_path="/renders/basic/job1/",
        ),
    ]


def test_client_resource_borrowing(audit_logger, performance_monitor, clients, render_nodes, render_jobs):
    """Test resource borrowing between clients based on demand and SLA tiers."""
    # Create resource partitioner with borrowing enabled
    resource_partitioner = ResourcePartitioner(
        audit_logger=audit_logger,
        performance_monitor=performance_monitor,
        allow_borrowing=True,
        borrowing_limit_percentage=20.0  # Allow up to 20% borrowed resources
    )
    
    # Add clients and nodes
    for client in clients:
        resource_partitioner.add_client(client)
    
    for node in render_nodes:
        resource_partitioner.add_node(node)
    
    # Calculate initial allocations based on SLA tiers without any active jobs
    allocations = resource_partitioner.allocate_resources()
    
    # Verify initial allocations follow SLA tier percentages
    premium_allocation = allocations["premium"]
    standard_allocation = allocations["standard"]
    basic_allocation = allocations["basic"]
    
    assert premium_allocation.allocated_percentage >= 50.0  # Premium gets at least 50%
    assert standard_allocation.allocated_percentage >= 30.0  # Standard gets at least 30%
    assert basic_allocation.allocated_percentage >= 10.0  # Basic gets at least 10%
    
    # Now simulate active jobs for each client
    client_job_counts = {"premium": 2, "standard": 1, "basic": 1}
    
    # Calculate demand percentage for each client
    premium_demand_pct = (client_job_counts["premium"] / sum(client_job_counts.values())) * 100.0
    standard_demand_pct = (client_job_counts["standard"] / sum(client_job_counts.values())) * 100.0
    basic_demand_pct = (client_job_counts["basic"] / sum(client_job_counts.values())) * 100.0
    
    # Set demand for each client
    resource_partitioner.update_client_demand("premium", premium_demand_pct)
    resource_partitioner.update_client_demand("standard", standard_demand_pct)
    resource_partitioner.update_client_demand("basic", basic_demand_pct)
    
    # Allocate resources based on demand and SLA tiers
    demand_allocations = resource_partitioner.allocate_resources()
    
    # Verify allocations reflect both SLA tiers and demand
    premium_allocation = demand_allocations["premium"]
    standard_allocation = demand_allocations["standard"]
    basic_allocation = demand_allocations["basic"]
    
    # Check borrowing relationships
    # Premium should borrow from basic since premium demand is higher than basic's
    assert "basic" in resource_partitioner.get_borrowed_from("premium")
    # Basic should lend to premium
    assert "premium" in resource_partitioner.get_lent_to("basic")
    
    # Check borrowed and lent percentages
    premium_borrowed = resource_partitioner.get_borrowed_percentage("premium")
    basic_lent = resource_partitioner.get_lent_percentage("basic")
    
    # Borrowed percentage should be positive for premium and zero for basic
    assert premium_borrowed > 0.0
    # Lent percentage should be positive for basic and zero for premium
    assert basic_lent > 0.0
    
    # Verify borrowing is within limits (20% in this case)
    assert premium_borrowed <= 20.0
    assert basic_lent <= 20.0
    
    # Now increase basic client demand significantly
    # Add more basic jobs
    basic_jobs = [
        RenderJob(
            id=f"basic_job{i}",
            client_id="basic",
            name=f"Basic Job {i}",
            status=RenderJobStatus.PENDING,
            job_type="simulation",
            priority=JobPriority.LOW,
            submission_time=datetime.now(),
            deadline=datetime.now() + timedelta(hours=12),
            estimated_duration_hours=1.0,
            progress=0.0,
            requires_gpu=False,
            memory_requirements_gb=16,
            cpu_requirements=4,
            scene_complexity=4,
            output_path=f"/renders/basic/job{i}/",
        )
        for i in range(2, 6)  # Adding 4 more basic jobs
    ]
    
    # Update job counts
    client_job_counts["basic"] = 5  # Now 5 basic jobs
    
    # Recalculate demand percentages
    premium_demand_pct = (client_job_counts["premium"] / sum(client_job_counts.values())) * 100.0
    standard_demand_pct = (client_job_counts["standard"] / sum(client_job_counts.values())) * 100.0
    basic_demand_pct = (client_job_counts["basic"] / sum(client_job_counts.values())) * 100.0
    
    # Update demand
    resource_partitioner.update_client_demand("premium", premium_demand_pct)
    resource_partitioner.update_client_demand("standard", standard_demand_pct)
    resource_partitioner.update_client_demand("basic", basic_demand_pct)
    
    # Reallocate resources
    new_allocations = resource_partitioner.allocate_resources()
    
    # Verify borrowing relationship has changed
    # Basic should no longer lend to premium
    assert "premium" not in resource_partitioner.get_lent_to("basic")
    # Premium should no longer borrow from basic
    assert "basic" not in resource_partitioner.get_borrowed_from("premium")
    
    # Verify basic client now gets more resources due to higher demand
    assert new_allocations["basic"].allocated_percentage > basic_allocation.allocated_percentage
    
    # Test with borrowing disabled
    resource_partitioner.allow_borrowing = False
    no_borrow_allocations = resource_partitioner.allocate_resources()
    
    # Verify no borrowing occurs when disabled
    for client_id in ["premium", "standard", "basic"]:
        assert resource_partitioner.get_borrowed_percentage(client_id) == 0.0
        assert resource_partitioner.get_lent_percentage(client_id) == 0.0
        assert not resource_partitioner.get_borrowed_from(client_id)
        assert not resource_partitioner.get_lent_to(client_id)
    
    # Verify audit logging occurred
    assert audit_logger.log_resource_allocation.call_count > 0
    
    # Verify performance metrics were updated
    assert performance_monitor.update_client_resource_metrics.call_count > 0


def test_borrowing_limit_variations(audit_logger, performance_monitor, clients, render_nodes):
    """Test different borrowing limit percentages and their effect on resource allocation."""
    # Create three resource partitioners with different borrowing limits
    partitioner_low = ResourcePartitioner(
        audit_logger=audit_logger,
        performance_monitor=performance_monitor,
        allow_borrowing=True,
        borrowing_limit_percentage=5.0  # Very low borrowing limit
    )
    
    partitioner_med = ResourcePartitioner(
        audit_logger=audit_logger,
        performance_monitor=performance_monitor,
        allow_borrowing=True,
        borrowing_limit_percentage=25.0  # Medium borrowing limit
    )
    
    partitioner_high = ResourcePartitioner(
        audit_logger=audit_logger,
        performance_monitor=performance_monitor,
        allow_borrowing=True,
        borrowing_limit_percentage=50.0  # High borrowing limit
    )
    
    partitioners = [partitioner_low, partitioner_med, partitioner_high]
    
    # Add clients and nodes to all partitioners
    for partitioner in partitioners:
        for client in clients:
            partitioner.add_client(client)
        
        for node in render_nodes:
            partitioner.add_node(node)
    
    # Set up a scenario where premium has very high demand, basic has very low
    for partitioner in partitioners:
        partitioner.update_client_demand("premium", 80.0)
        partitioner.update_client_demand("standard", 15.0)
        partitioner.update_client_demand("basic", 5.0)
    
    # Calculate allocations for each partitioner
    allocations_low = partitioner_low.allocate_resources()
    allocations_med = partitioner_med.allocate_resources()
    allocations_high = partitioner_high.allocate_resources()
    
    # Get borrowed percentages for premium client
    borrowed_low = partitioner_low.get_borrowed_percentage("premium")
    borrowed_med = partitioner_med.get_borrowed_percentage("premium")
    borrowed_high = partitioner_high.get_borrowed_percentage("premium")
    
    # Verify borrowed percentage respects the configured limit
    assert borrowed_low <= 5.0
    assert borrowed_med <= 25.0
    assert borrowed_high <= 50.0
    
    # Verify higher borrowing limits result in more resources for premium client
    # (which has the highest demand)
    assert allocations_low["premium"].allocated_percentage < allocations_med["premium"].allocated_percentage
    assert allocations_med["premium"].allocated_percentage < allocations_high["premium"].allocated_percentage