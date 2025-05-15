"""
Example script showing how to initialize and use the RenderFarmManager.

This example demonstrates:
1. Basic RenderFarmManager initialization and usage
2. Node specialization and job-to-node matching
3. Performance metrics for specialized job placement
"""

import random
from datetime import datetime, timedelta

from render_farm_manager.core.manager import RenderFarmManager
from render_farm_manager.scheduling.deadline_scheduler import DeadlineScheduler
from render_farm_manager.resource_management.resource_partitioner import ResourcePartitioner
from render_farm_manager.node_specialization.specialization_manager import NodeSpecializationManager
from render_farm_manager.progressive_result.progressive_renderer import ProgressiveRenderer
from render_farm_manager.energy_optimization.energy_optimizer import EnergyOptimizer
from render_farm_manager.utils.logging import AuditLogger, PerformanceMonitor
from render_farm_manager.core.models import (
    Client, 
    RenderNode, 
    NodeCapabilities, 
    RenderJob, 
    JobPriority, 
    RenderJobStatus
)

# Example of basic farm setup
def setup_basic_render_farm():
    """Setup a simple render farm with one client and one node."""
    # Initialize components
    audit_logger = AuditLogger()
    performance_monitor = PerformanceMonitor(audit_logger)
    
    # Initialize RenderFarmManager
    manager = RenderFarmManager()
    
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


# Example of creating a specialized render farm with optimized job matching
def create_specialized_farm_manager():
    """Create a render farm manager with specialized nodes for different job types."""
    # Create the manager
    farm_manager = RenderFarmManager()
    
    # Add clients
    clients = [
        Client(
            id="premium_client",
            name="Premium VFX Studio",
            sla_tier="premium",
            guaranteed_resources=50,
            max_resources=100,
        ),
        Client(
            id="standard_client",
            name="Standard Animation Studio",
            sla_tier="standard",
            guaranteed_resources=25,
            max_resources=75,
        ),
        Client(
            id="basic_client",
            name="Independent Artist",
            sla_tier="basic",
            guaranteed_resources=10,
            max_resources=30,
        ),
    ]
    
    for client in clients:
        farm_manager.add_client(client)
    
    # Add specialized nodes
    # GPU rendering nodes
    for i in range(1, 6):
        node = RenderNode(
            id=f"gpu_node_{i}",
            name=f"GPU Rendering Node {i}",
            status="online",
            capabilities=NodeCapabilities(
                cpu_cores=32,
                memory_gb=128,
                gpu_model="NVIDIA RTX A6000",
                gpu_count=4,
                gpu_memory_gb=48,
                gpu_compute_capability=8.6,
                storage_gb=2000,
                specialized_for=["gpu_rendering", "animation_rendering", "vfx_rendering", "lighting_rendering"],
            ),
            power_efficiency_rating=85,
        )
        farm_manager.add_node(node)
    
    # CPU simulation nodes
    for i in range(1, 6):
        node = RenderNode(
            id=f"cpu_node_{i}",
            name=f"CPU Simulation Node {i}",
            status="online",
            capabilities=NodeCapabilities(
                cpu_cores=64,
                memory_gb=256,
                gpu_model="NVIDIA RTX A4000",
                gpu_count=1,
                gpu_memory_gb=16,
                gpu_compute_capability=8.6,
                storage_gb=4000,
                specialized_for=["cpu_rendering", "simulation", "physics", "compositing"],
            ),
            power_efficiency_rating=78,
        )
        farm_manager.add_node(node)
    
    # Memory-intensive nodes
    for i in range(1, 4):
        node = RenderNode(
            id=f"memory_node_{i}",
            name=f"Memory-Intensive Node {i}",
            status="online",
            capabilities=NodeCapabilities(
                cpu_cores=48,
                memory_gb=1024,
                gpu_model="NVIDIA RTX A5000",
                gpu_count=2,
                gpu_memory_gb=24,
                gpu_compute_capability=8.6,
                storage_gb=8000,
                specialized_for=["memory_intensive", "scene_assembly", "fluid_simulation"],
            ),
            power_efficiency_rating=72,
        )
        farm_manager.add_node(node)
    
    # Return the initialized manager
    return farm_manager


def submit_specialized_jobs(farm_manager):
    """Submit specialized jobs for testing node specialization efficiency."""
    now = datetime.now()
    client_ids = list(farm_manager.clients.keys())
    
    # Create specialized test jobs
    jobs = []
    
    # GPU jobs - these should match with GPU nodes
    for i in range(10):
        jobs.append(
            RenderJob(
                id=f"gpu-job-{i}",
                name=f"GPU Job {i}",
                client_id=random.choice(client_ids),
                status=RenderJobStatus.PENDING,
                job_type="animation" if i % 2 == 0 else "vfx",
                priority=JobPriority.HIGH,
                submission_time=now - timedelta(hours=random.randint(0, 5)),
                deadline=now + timedelta(hours=random.randint(12, 48)),
                estimated_duration_hours=random.randint(4, 12),
                progress=0.0,
                requires_gpu=True,
                memory_requirements_gb=random.randint(32, 96),
                cpu_requirements=random.randint(8, 16),
                scene_complexity=random.randint(6, 10),
                dependencies=[],
                assigned_node_id=None,
                output_path=f"/renders/gpu-job-{i}/",
                error_count=0,
                can_be_preempted=True,
                supports_progressive_output=True,
            )
        )
    
    # CPU jobs - these should match with CPU nodes
    for i in range(10):
        jobs.append(
            RenderJob(
                id=f"cpu-job-{i}",
                name=f"CPU Job {i}",
                client_id=random.choice(client_ids),
                status=RenderJobStatus.PENDING,
                job_type="simulation" if i % 2 == 0 else "compositing",
                priority=JobPriority.MEDIUM,
                submission_time=now - timedelta(hours=random.randint(0, 5)),
                deadline=now + timedelta(hours=random.randint(24, 72)),
                estimated_duration_hours=random.randint(6, 18),
                progress=0.0,
                requires_gpu=False,
                memory_requirements_gb=random.randint(16, 128),
                cpu_requirements=random.randint(16, 64),
                scene_complexity=random.randint(4, 8),
                dependencies=[],
                assigned_node_id=None,
                output_path=f"/renders/cpu-job-{i}/",
                error_count=0,
                can_be_preempted=True,
                supports_progressive_output=False,
            )
        )
    
    # Memory-intensive jobs - these should match with Memory nodes
    for i in range(5):
        jobs.append(
            RenderJob(
                id=f"mem-job-{i}",
                name=f"Memory Job {i}",
                client_id=random.choice(client_ids),
                status=RenderJobStatus.PENDING,
                job_type="scene_assembly",
                priority=JobPriority.MEDIUM,
                submission_time=now - timedelta(hours=random.randint(0, 5)),
                deadline=now + timedelta(hours=random.randint(24, 96)),
                estimated_duration_hours=random.randint(6, 15),
                progress=0.0,
                requires_gpu=False,
                memory_requirements_gb=random.randint(256, 1024),
                cpu_requirements=random.randint(16, 32),
                scene_complexity=random.randint(5, 9),
                dependencies=[],
                assigned_node_id=None,
                output_path=f"/renders/mem-job-{i}/",
                error_count=0,
                can_be_preempted=True,
                supports_progressive_output=False,
            )
        )
    
    # Submit all jobs
    for job in jobs:
        farm_manager.submit_job(job)
    
    return len(jobs)


def calculate_specialization_efficiency(farm_manager):
    """Calculate the specialization efficiency of the assigned jobs."""
    gpu_jobs_on_gpu_nodes = 0
    cpu_jobs_on_cpu_nodes = 0
    mem_jobs_on_mem_nodes = 0
    total_assigned = 0
    
    for job_id, job in farm_manager.jobs.items():
        if job.status == RenderJobStatus.RUNNING and job.assigned_node_id:
            total_assigned += 1
            node = farm_manager.nodes[job.assigned_node_id]
            
            if job_id.startswith("gpu-job") and "gpu_rendering" in node.capabilities.specialized_for:
                gpu_jobs_on_gpu_nodes += 1
            elif job_id.startswith("cpu-job") and "cpu_rendering" in node.capabilities.specialized_for:
                cpu_jobs_on_cpu_nodes += 1
            elif job_id.startswith("mem-job") and "memory_intensive" in node.capabilities.specialized_for:
                mem_jobs_on_mem_nodes += 1
    
    # Calculate specialization efficiency
    if total_assigned > 0:
        specialization_efficiency = (gpu_jobs_on_gpu_nodes + cpu_jobs_on_cpu_nodes + mem_jobs_on_mem_nodes) / total_assigned * 100
    else:
        specialization_efficiency = 0
    
    # Calculate per-type efficiencies
    gpu_efficiency = gpu_jobs_on_gpu_nodes / sum(1 for j in farm_manager.jobs.values() if j.id.startswith("gpu-job") and j.status == RenderJobStatus.RUNNING) * 100 if gpu_jobs_on_gpu_nodes > 0 else 0
    cpu_efficiency = cpu_jobs_on_cpu_nodes / sum(1 for j in farm_manager.jobs.values() if j.id.startswith("cpu-job") and j.status == RenderJobStatus.RUNNING) * 100 if cpu_jobs_on_cpu_nodes > 0 else 0
    mem_efficiency = mem_jobs_on_mem_nodes / sum(1 for j in farm_manager.jobs.values() if j.id.startswith("mem-job") and j.status == RenderJobStatus.RUNNING) * 100 if mem_jobs_on_mem_nodes > 0 else 0
    
    return {
        "overall_efficiency": specialization_efficiency,
        "gpu_efficiency": gpu_efficiency,
        "cpu_efficiency": cpu_efficiency,
        "mem_efficiency": mem_efficiency,
        "gpu_jobs_on_gpu_nodes": gpu_jobs_on_gpu_nodes,
        "cpu_jobs_on_cpu_nodes": cpu_jobs_on_cpu_nodes,
        "mem_jobs_on_mem_nodes": mem_jobs_on_mem_nodes,
        "total_assigned": total_assigned,
    }


# Example of monitoring system status
def monitor_farm_status(manager):
    """Get and display the current farm status."""
    # Get overall farm status
    farm_status = manager.get_farm_status()
    print(f"Total nodes: {farm_status['total_nodes']}")
    print(f"Online nodes: {farm_status['nodes_by_status'].get('online', 0)}")
    print(f"Active jobs: {farm_status['jobs_by_status'].get('running', 0)}")
    
    # Get client statuses
    for client_id in manager.clients:
        client_status = manager.get_client_status(client_id)
        print(f"Client {client_id} resource usage: {client_status['current_resource_usage']:.1f}%")
        print(f"Active jobs: {len(client_status['active_jobs'])}")
    
    # Analyze node specialization
    efficiency = calculate_specialization_efficiency(manager)
    print(f"\nNode Specialization Efficiency: {efficiency['overall_efficiency']:.2f}%")
    print(f"GPU efficiency: {efficiency['gpu_efficiency']:.2f}%")
    print(f"CPU efficiency: {efficiency['cpu_efficiency']:.2f}%")
    print(f"Memory efficiency: {efficiency['mem_efficiency']:.2f}%")


def run_specialized_job_demo():
    """Run a demo of the specialized job scheduler."""
    print("Initializing Specialized Render Farm Manager...")
    farm_manager = create_specialized_farm_manager()
    
    print(f"Added {len(farm_manager.clients)} clients")
    print(f"Added {len(farm_manager.nodes)} specialized render nodes")
    
    print("\nSubmitting specialized jobs...")
    job_count = submit_specialized_jobs(farm_manager)
    print(f"Submitted {job_count} specialized jobs")
    
    print("\nRunning scheduling cycle...")
    results = farm_manager.run_scheduling_cycle()
    print(f"Scheduled {results['jobs_scheduled']} jobs")
    print(f"Resource utilization: {results['utilization_percentage']:.2f}%")
    
    print("\nCalculating specialization efficiency...")
    efficiency = calculate_specialization_efficiency(farm_manager)
    
    print("\nNode Specialization Results:")
    print(f"Overall specialization efficiency: {efficiency['overall_efficiency']:.2f}%")
    print(f"GPU job efficiency: {efficiency['gpu_efficiency']:.2f}%")
    print(f"CPU job efficiency: {efficiency['cpu_efficiency']:.2f}%")
    print(f"Memory job efficiency: {efficiency['mem_efficiency']:.2f}%")
    print(f"GPU jobs on GPU nodes: {efficiency['gpu_jobs_on_gpu_nodes']}")
    print(f"CPU jobs on CPU nodes: {efficiency['cpu_jobs_on_cpu_nodes']}")
    print(f"Memory jobs on Memory nodes: {efficiency['mem_jobs_on_mem_nodes']}")
    print(f"Total jobs assigned: {efficiency['total_assigned']}")
    
    return farm_manager


# Main function to run the examples
if __name__ == "__main__":
    print("=== BASIC RENDER FARM EXAMPLE ===")
    basic_farm = setup_basic_render_farm()
    
    print("\n=== SPECIALIZED FARM EXAMPLE ===")
    specialized_farm = run_specialized_job_demo()