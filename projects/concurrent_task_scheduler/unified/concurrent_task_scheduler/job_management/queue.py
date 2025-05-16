"""Queue management for long-running simulation jobs."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any

from common.core.models import (
    Priority,
    Result,
)
from common.job_management.queue import (
    JobQueue as CommonJobQueue,
    QueuePolicy,
    FairnessMetric,
    PreemptionAction,
    PreemptionTrigger,
    PreemptionPolicy,
    QueueStats,
)

from concurrent_task_scheduler.models import (
    Simulation,
    SimulationStatus,
)
from concurrent_task_scheduler.models.utils import generate_id

logger = logging.getLogger(__name__)


# Using QueuePolicy, FairnessMetric from common.job_management.queue

# Map SimulationPriority to common Priority for compatibility
def map_simulation_priority_to_common(sim_priority) -> Priority:
    """Map simulation priority to common priority."""
    mapping = {
        "critical": Priority.CRITICAL,
        "high": Priority.HIGH, 
        "medium": Priority.MEDIUM,
        "low": Priority.LOW,
        "background": Priority.BACKGROUND
    }
    
    # Handle both string and enum cases
    if hasattr(sim_priority, "value"):
        return mapping.get(sim_priority.value.lower(), Priority.MEDIUM)
    else:
        return mapping.get(str(sim_priority).lower(), Priority.MEDIUM)


# Using QueueStats from common.job_management.queue


# Using QueuedJob from common.job_management.queue


# Using PreemptionAction, PreemptionTrigger, PreemptionPolicy from common.job_management.queue


class JobQueue(CommonJobQueue[Simulation]):
    """Queue for managing simulation jobs.
    
    This extends the common JobQueue implementation with simulation-specific functionality.
    """

    def __init__(
        self,
        policy: QueuePolicy = QueuePolicy.WEIGHTED,
        preemption_policy: Optional[PreemptionPolicy] = None,
    ):
        super().__init__(policy, preemption_policy)
    
    def enqueue(self, simulation: Simulation) -> Result[bool]:
        """Add a simulation to the queue.
        
        This overrides the parent method to maintain backward compatibility with tests.
        """
        # Map simulation priority to common priority
        original_priority = simulation.priority
        simulation.priority = map_simulation_priority_to_common(original_priority)
        
        result = super().enqueue(simulation)
        
        # Restore original priority for compatibility
        simulation.priority = original_priority
        
        # Return string result for backward compatibility
        if result.success:
            return f"Simulation {simulation.id} added to queue"
        else:
            return result.error
    
    def dequeue(self) -> Optional[Simulation]:
        """Get the highest priority simulation from the queue."""
        simulation = super().dequeue()
        return simulation
    
    def remove(self, simulation_id: str) -> bool:
        """Remove a specific simulation from the queue.
        
        This overrides the parent method to maintain backward compatibility with tests.
        """
        result = super().remove(simulation_id)
        return result.success
    
    def update_priority(self, simulation_id: str, new_priority) -> bool:
        """Update the priority of a queued simulation.
        
        This overrides the parent method to maintain backward compatibility with tests.
        """
        # Map simulation priority to common priority
        common_priority = map_simulation_priority_to_common(new_priority)
        
        result = super().update_priority(simulation_id, common_priority)
        return result.success
    
    def get_wait_time_estimate(self, simulation: Simulation) -> timedelta:
        """Estimate wait time for a new simulation."""
        # Map simulation priority to common priority temporarily
        original_priority = simulation.priority
        common_priority = map_simulation_priority_to_common(original_priority)
        simulation.priority = common_priority
        
        estimate = super().get_wait_time_estimate(simulation)
        
        # Restore original priority
        simulation.priority = original_priority
        
        return estimate