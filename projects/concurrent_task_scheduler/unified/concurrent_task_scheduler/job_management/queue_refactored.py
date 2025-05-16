"""Queue management for long-running simulation jobs."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union

from common.core.models import Priority, Result
from common.job_management.queue import (
    JobQueue as CommonJobQueue,
    QueuePolicy,
    FairnessMetric,
    PreemptionAction,
    PreemptionTrigger,
    PreemptionPolicy,
    QueueStats,
)

from concurrent_task_scheduler.models.simulation import (
    Simulation,
    SimulationStatus,
    SimulationPriority,
)


def map_simulation_priority_to_common(sim_priority) -> Priority:
    """
    Map simulation priority to common priority.
    
    Args:
        sim_priority: Simulation priority value
        
    Returns:
        Corresponding common Priority enum value
    """
    # If already a Priority enum, return as is
    if isinstance(sim_priority, Priority):
        return sim_priority
    
    # Try to convert SimulationPriority to Priority
    if hasattr(sim_priority, 'to_common_priority'):
        return sim_priority.to_common_priority()
    
    # Map string or enum values
    mapping = {
        "critical": Priority.CRITICAL,
        "high": Priority.HIGH, 
        "medium": Priority.MEDIUM,
        "low": Priority.LOW,
        "background": Priority.BACKGROUND,
    }
    
    # Handle both string and enum cases
    if hasattr(sim_priority, "value"):
        return mapping.get(sim_priority.value.lower(), Priority.MEDIUM)
    else:
        return mapping.get(str(sim_priority).lower(), Priority.MEDIUM)


def map_common_priority_to_simulation(common_priority) -> SimulationPriority:
    """
    Map common priority to simulation priority.
    
    Args:
        common_priority: Common priority value
        
    Returns:
        Corresponding SimulationPriority enum value
    """
    # If already a SimulationPriority enum, return as is
    if isinstance(common_priority, SimulationPriority):
        return common_priority
    
    # Try to convert using SimulationPriority's class method
    if hasattr(SimulationPriority, 'from_common_priority'):
        return SimulationPriority.from_common_priority(common_priority)
    
    # Map string or enum values
    mapping = {
        "critical": SimulationPriority.CRITICAL,
        "high": SimulationPriority.HIGH, 
        "medium": SimulationPriority.MEDIUM,
        "low": SimulationPriority.LOW,
        "background": SimulationPriority.BACKGROUND,
    }
    
    # Handle both string and enum cases
    if hasattr(common_priority, "value"):
        return mapping.get(common_priority.value.lower(), SimulationPriority.MEDIUM)
    else:
        return mapping.get(str(common_priority).lower(), SimulationPriority.MEDIUM)


class JobQueue(CommonJobQueue[Simulation]):
    """
    Queue for managing simulation jobs.
    
    This extends the common JobQueue implementation with simulation-specific functionality.
    """
    
    def __init__(
        self,
        policy: QueuePolicy = QueuePolicy.WEIGHTED,
        preemption_policy: Optional[PreemptionPolicy] = None,
    ):
        """
        Initialize the job queue.
        
        Args:
            policy: Queue policy to use
            preemption_policy: Optional preemption policy
        """
        super().__init__(policy, preemption_policy)
    
    def enqueue(self, simulation: Simulation) -> Result[bool]:
        """
        Add a simulation to the queue.
        
        Args:
            simulation: The simulation to enqueue
            
        Returns:
            Result indicating success or failure
        """
        # Store original priority
        original_priority = simulation.priority
        
        # Map simulation priority to common priority
        simulation.priority = map_simulation_priority_to_common(original_priority)
        
        # Call parent implementation
        result = super().enqueue(simulation)
        
        # Restore original priority for compatibility
        simulation.priority = original_priority
        
        # Return user-friendly result for backward compatibility
        if result.success:
            return Result.ok(True)
        else:
            return result
    
    def dequeue(self) -> Optional[Simulation]:
        """
        Get the highest priority simulation from the queue.
        
        Returns:
            The next simulation to process, or None if queue is empty
        """
        simulation = super().dequeue()
        
        # If we got a simulation, restore its original priority format if needed
        if simulation and isinstance(simulation.priority, Priority):
            simulation.priority = map_common_priority_to_simulation(simulation.priority)
        
        return simulation
    
    def remove(self, simulation_id: str) -> Result[bool]:
        """
        Remove a specific simulation from the queue.
        
        Args:
            simulation_id: ID of the simulation to remove
            
        Returns:
            Result indicating success or failure
        """
        result = super().remove(simulation_id)
        return result
    
    def update_priority(self, simulation_id: str, new_priority) -> Result[bool]:
        """
        Update the priority of a queued simulation.
        
        Args:
            simulation_id: ID of the simulation
            new_priority: New priority value
            
        Returns:
            Result indicating success or failure
        """
        # Map simulation priority to common priority
        common_priority = map_simulation_priority_to_common(new_priority)
        
        # Call parent implementation
        result = super().update_priority(simulation_id, common_priority)
        
        # If successful and the simulation is still in the queue, restore its priority format
        if result.success:
            for i, job in enumerate(self.queued_jobs):
                if job.job.id == simulation_id:
                    job.job.priority = new_priority
                    break
        
        return result
    
    def get_wait_time_estimate(self, simulation: Simulation) -> timedelta:
        """
        Estimate wait time for a new simulation.
        
        Args:
            simulation: The simulation to estimate for
            
        Returns:
            Estimated wait time
        """
        # Store original priority
        original_priority = simulation.priority
        
        # Map simulation priority to common priority
        common_priority = map_simulation_priority_to_common(original_priority)
        simulation.priority = common_priority
        
        # Call parent implementation
        estimate = super().get_wait_time_estimate(simulation)
        
        # Restore original priority
        simulation.priority = original_priority
        
        return estimate
    
    def get_simulation_queue_position(self, simulation_id: str) -> int:
        """
        Get the position of a simulation in the queue.
        
        Args:
            simulation_id: ID of the simulation
            
        Returns:
            Position in the queue (0-based), or -1 if not found
        """
        for i, job in enumerate(self.sorted_jobs()):
            if job.job.id == simulation_id:
                return i
        return -1
    
    def get_queue_stats(self) -> QueueStats:
        """
        Get statistics for the current queue.
        
        Returns:
            Queue statistics
        """
        stats = super().get_queue_stats()
        
        # Add simulation-specific stats
        stats.metadata["scientific_simulations"] = sum(
            1 for job in self.queued_jobs
            if hasattr(job.job, "scientific_promise") and job.job.scientific_promise > 0.7
        )
        
        return stats