"""Example usage of the dependency tracking system."""

from typing import Set

from common.core.models import BaseJob, JobStatus, Priority
from common.dependency_tracking.graph import DependencyGraph, GraphNodeType
from common.dependency_tracking.tracker import DependencyTracker
from common.dependency_tracking.workflow import WorkflowManager

def test_dependency_tracker():
    """Test the dependency tracker functionality."""
    # Create a tracker
    tracker = DependencyTracker()
    
    # Create a graph for a simulation
    simulation_id = "simulation-1"
    result = tracker.create_graph(simulation_id)
    if not result.success:
        print(f"Failed to create graph: {result.error}")
        return
    
    # Add stages (nodes)
    graph = tracker.get_graph(simulation_id)
    graph.add_node("stage-1", GraphNodeType.STAGE, {"name": "Stage 1"})
    graph.add_node("stage-2", GraphNodeType.STAGE, {"name": "Stage 2"})
    graph.add_node("stage-3", GraphNodeType.STAGE, {"name": "Stage 3"})
    
    # Add dependencies
    tracker.add_dependency(simulation_id, "stage-1", "stage-2")
    tracker.add_dependency(simulation_id, "stage-2", "stage-3")
    
    # Check for cycles
    cycle_result = tracker.has_cycle()
    print(f"Has cycle: {cycle_result.value is not None}")
    
    # Get ready stages
    ready_stages = tracker.get_ready_stages(simulation_id)
    print(f"Ready stages: {ready_stages}")
    
    # Update a stage status to completed
    tracker.update_stage_status(simulation_id, "stage-1", JobStatus.COMPLETED)
    
    # Check if stage-2 is ready
    is_ready = tracker.is_stage_ready(simulation_id, "stage-2", {"stage-1"})
    print(f"Stage 2 is ready: {is_ready}")
    
    # Get blocking stages for stage-3
    blocking = tracker.get_blocking_stages(simulation_id, "stage-3")
    print(f"Blocking stages for stage-3: {blocking}")
    
    # Get execution plan
    plan_result = tracker.get_execution_plan(simulation_id)
    if plan_result.success:
        print(f"Execution plan: {plan_result.value}")
    
    # Validate the graph
    errors = tracker.validate_simulation(simulation_id)
    if errors:
        print(f"Validation errors: {errors}")
    else:
        print("Graph is valid")

def test_workflow_manager():
    """Test the workflow manager functionality."""
    # Create jobs
    jobs = {
        "job-1": BaseJob(
            id="job-1",
            name="Stage 1",
            status=JobStatus.PENDING,
            priority=Priority.MEDIUM,
        ),
        "job-2": BaseJob(
            id="job-2",
            name="Stage 2",
            status=JobStatus.PENDING,
            priority=Priority.MEDIUM,
        ),
        "job-3": BaseJob(
            id="job-3",
            name="Stage 3",
            status=JobStatus.PENDING,
            priority=Priority.MEDIUM,
        ),
    }
    
    # Create workflow manager
    manager = WorkflowManager()
    
    # Create a linear workflow
    owner_id = "owner-1"
    result = manager.create_linear_workflow(
        owner_id=owner_id,
        stage_names=["Stage 1", "Stage 2", "Stage 3"],
        jobs=jobs,
    )
    
    if not result.success:
        print(f"Failed to create workflow: {result.error}")
        return
    
    instance = result.value
    print(f"Created workflow instance: {instance.id}")
    
    # Get next jobs to execute
    next_result = manager.get_next_jobs(instance.id, jobs)
    if next_result.success:
        next_jobs = next_result.value
        print(f"Next jobs to execute: {next_jobs}")
    
    # Update job status
    for job_id in next_jobs:
        update_result = manager.update_job_status(
            instance.id,
            job_id,
            JobStatus.COMPLETED,
            jobs,
        )
        
        if update_result.success:
            print(f"Updated job status: {job_id} -> COMPLETED")
    
    # Get next jobs after completing the first ones
    next_result = manager.get_next_jobs(instance.id, jobs)
    if next_result.success:
        next_jobs = next_result.value
        print(f"Next jobs to execute: {next_jobs}")
    
    # Get workflow status
    status_result = manager.get_workflow_status(instance.id)
    if status_result.success:
        status = status_result.value
        print(f"Workflow status: {status}")

if __name__ == "__main__":
    print("Testing dependency tracker...")
    test_dependency_tracker()
    
    print("\nTesting workflow manager...")
    test_workflow_manager()