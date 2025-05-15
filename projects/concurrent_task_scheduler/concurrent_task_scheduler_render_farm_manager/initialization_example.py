"""Example script showing how to initialize and use the RenderFarmManager."""

from datetime import datetime, timedelta
from render_farm_manager.core.manager import RenderFarmManager
from render_farm_manager.scheduling.deadline_scheduler import DeadlineScheduler
from render_farm_manager.resource_management.resource_partitioner import ResourcePartitioner
from render_farm_manager.node_specialization.specialization_manager import NodeSpecializationManager
from render_farm_manager.progressive_result.progressive_renderer import ProgressiveRenderer
from render_farm_manager.energy_optimization.energy_optimizer import EnergyOptimizer
from render_farm_manager.utils.logging import AuditLogger, PerformanceMonitor
from render_farm_manager.core.models import Client, RenderNode, NodeCapabilities, RenderJob, JobPriority, RenderJobStatus

# Initialize components
audit_logger = AuditLogger()
performance_monitor = PerformanceMonitor(audit_logger)

# Optional: Initialize components with custom parameters
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

# Initialize RenderFarmManager with default components
manager = RenderFarmManager()

# Or initialize with custom components
custom_manager = RenderFarmManager(
    scheduler=scheduler,
    resource_manager=resource_manager,
    node_specializer=NodeSpecializationManager(audit_logger, performance_monitor),
    progressive_renderer=ProgressiveRenderer(audit_logger, performance_monitor),
    energy_optimizer=EnergyOptimizer(audit_logger, performance_monitor),
    audit_logger=audit_logger,
    performance_monitor=performance_monitor
)

# All parameters are optional - the manager will create defaults for any missing components
partial_custom_manager = RenderFarmManager(
    scheduler=scheduler,
    resource_manager=resource_manager
)

# Example of adding resources and submitting jobs
def setup_render_farm():
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
    
    return manager

# Example of monitoring system status
def monitor_farm_status(manager):
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

# Uncomment to run the examples
# if __name__ == "__main__":
#     farm_manager = setup_render_farm()
#     monitor_farm_status(farm_manager)