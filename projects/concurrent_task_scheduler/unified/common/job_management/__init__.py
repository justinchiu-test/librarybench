"""
Job management package for the unified concurrent task scheduler.

This package provides functionality for managing and scheduling jobs that can be used
by both the render farm manager and scientific computing implementations.
"""

# Queue management
from common.job_management.queue import (
    JobQueue,
    QueuePolicy,
    FairnessMetric,
    QueuedJob,
    QueueStats,
    PreemptionAction,
    PreemptionTrigger,
    PreemptionPolicy,
)

# Job scheduling
from common.job_management.scheduler import JobScheduler

# Priority management
from common.job_management.prioritization import (
    PriorityManager,
    PriorityPolicy,
    PriorityInheritanceMode,
)