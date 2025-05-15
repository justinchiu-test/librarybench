"""
Job queue management for the unified concurrent task scheduler.

This module provides a common job queue implementation that can be used by both
the render farm manager and scientific computing implementations.
"""

from __future__ import annotations

import heapq
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Generic, TypeVar, Union, Any

from common.core.models import (
    BaseJob,
    JobStatus,
    Priority,
    Result,
)

logger = logging.getLogger(__name__)

# Type variable for job types
T = TypeVar("T", bound=BaseJob)


class QueuePolicy(str, Enum):
    """Policies for managing the job queue."""

    FIFO = "fifo"  # First in, first out
    PRIORITY = "priority"  # Strict priority ordering
    FAIR = "fair"  # Fair sharing between users/projects
    DEADLINE = "deadline"  # Deadline-driven ordering
    WEIGHTED = "weighted"  # Weighted combination of factors


class FairnessMetric(str, Enum):
    """Metrics for evaluating fairness in resource allocation."""

    CPU_TIME = "cpu_time"  # Total CPU time allocated
    WAIT_TIME = "wait_time"  # Queue wait time
    JOB_COUNT = "job_count"  # Number of jobs run
    RESOURCE_SHARE = "resource_share"  # Share of total resources
    WEIGHTED = "weighted"  # Weighted combination of metrics


class PreemptionAction(str, Enum):
    """Actions that can be taken when preemption is triggered."""

    CHECKPOINT_AND_STOP = "checkpoint_and_stop"  # Create checkpoint and stop job
    MIGRATE = "migrate"  # Try to migrate job to other resources
    REQUEUE = "requeue"  # Move job back to queue
    CONTINUE_LIMITED = "continue_limited"  # Continue with limited resources
    CANCEL = "cancel"  # Cancel job entirely


class PreemptionTrigger(str, Enum):
    """Triggers for job preemption."""

    HIGHER_PRIORITY = "higher_priority"  # Higher priority job needs resources
    MAINTENANCE = "maintenance"  # System maintenance
    RESOURCE_SHORTAGE = "resource_shortage"  # Insufficient resources
    FAIRNESS = "fairness"  # Fairness policy enforcement
    ADMIN = "admin"  # Administrative action
    DEADLINE = "deadline"  # Job exceeded deadline


class QueuedJob(Generic[T]):
    """A job in the queue."""

    def __init__(self, job: T, submit_time: datetime):
        self.job = job
        self.submit_time = submit_time
        self.priority_updates: List[Tuple[datetime, Priority]] = [
            (submit_time, job.priority)
        ]
        self.effective_priority = job.priority
        self.last_priority_decay = submit_time
        self.preemption_count = 0
        self.last_preemption_time: Optional[datetime] = None
        self.estimated_start_time: Optional[datetime] = None
        self.user_notified = False
        self.retry_count = 0
    
    def wait_time(self) -> timedelta:
        """Get the current wait time for this job."""
        return datetime.now() - self.submit_time
    
    def update_priority(self, new_priority: Priority) -> None:
        """Update the job's priority."""
        if new_priority != self.job.priority:
            self.job.priority = new_priority
            self.priority_updates.append((datetime.now(), new_priority))
            self.effective_priority = new_priority
    
    def record_preemption(self) -> None:
        """Record that this job was preempted."""
        self.preemption_count += 1
        self.last_preemption_time = datetime.now()
    
    def get_priority_history(self) -> List[Tuple[datetime, Priority]]:
        """Get the job's priority history."""
        return self.priority_updates.copy()
    
    def __lt__(self, other: QueuedJob) -> bool:
        """Compare jobs for priority queue ordering."""
        # First compare by effective priority (CRITICAL is highest)
        if self.effective_priority != other.effective_priority:
            # Higher priority (CRITICAL) comes first
            priority_order = {
                Priority.CRITICAL: 0,
                Priority.HIGH: 1,
                Priority.MEDIUM: 2,
                Priority.LOW: 3,
                Priority.BACKGROUND: 4
            }
            return priority_order[self.effective_priority] < priority_order[other.effective_priority]
        
        # For same priority, older jobs come first (FIFO)
        return self.submit_time < other.submit_time


class QueueStats:
    """Statistics for a job queue."""

    def __init__(self):
        self.total_jobs_submitted = 0
        self.total_jobs_started = 0
        self.total_jobs_completed = 0
        self.total_jobs_failed = 0
        self.total_jobs_cancelled = 0
        self.total_wait_time = timedelta()
        self.avg_wait_time = timedelta()
        self.max_wait_time = timedelta()
        self.current_queue_length = 0
        self.peak_queue_length = 0
        self.by_priority: Dict[Priority, int] = {
            priority: 0 for priority in Priority
        }
        self.by_user: Dict[str, int] = {}
        self.by_project: Dict[str, int] = {}
        self.last_updated = datetime.now()
    
    def update_on_submit(self, job: BaseJob) -> None:
        """Update stats when a job is submitted."""
        self.total_jobs_submitted += 1
        self.current_queue_length += 1
        self.peak_queue_length = max(self.peak_queue_length, self.current_queue_length)
        self.by_priority[job.priority] += 1
        
        self.by_user[job.owner] = self.by_user.get(job.owner, 0) + 1
        self.by_project[job.project] = self.by_project.get(job.project, 0) + 1
        self.last_updated = datetime.now()
    
    def update_on_start(self, job: BaseJob, submit_time: datetime) -> None:
        """Update stats when a job starts running."""
        self.total_jobs_started += 1
        self.current_queue_length -= 1
        
        wait_time = datetime.now() - submit_time
        self.total_wait_time += wait_time
        self.max_wait_time = max(self.max_wait_time, wait_time)
        
        if self.total_jobs_started > 0:
            self.avg_wait_time = self.total_wait_time / self.total_jobs_started
        
        self.last_updated = datetime.now()
    
    def update_on_complete(self, job: BaseJob) -> None:
        """Update stats when a job completes."""
        self.total_jobs_completed += 1
        self.last_updated = datetime.now()
    
    def update_on_fail(self, job: BaseJob) -> None:
        """Update stats when a job fails."""
        self.total_jobs_failed += 1
        self.last_updated = datetime.now()
    
    def update_on_cancel(self, job: BaseJob) -> None:
        """Update stats when a job is cancelled."""
        self.total_jobs_cancelled += 1
        self.current_queue_length -= 1
        self.last_updated = datetime.now()


class PreemptionPolicy:
    """Policy for job preemption."""

    def __init__(
        self,
        max_preemptions_per_day: Dict[Priority, int] = None,
        min_runtime_before_preemption: timedelta = timedelta(hours=1),
        protection_after_preemption: timedelta = timedelta(hours=6),
        checkpoint_before_preemption: bool = True,
    ):
        if max_preemptions_per_day is None:
            self.max_preemptions_per_day = {
                Priority.CRITICAL: 0,  # Cannot be preempted
                Priority.HIGH: 1,
                Priority.MEDIUM: 2,
                Priority.LOW: 4,
                Priority.BACKGROUND: 8,
            }
        else:
            self.max_preemptions_per_day = max_preemptions_per_day
        
        self.min_runtime_before_preemption = min_runtime_before_preemption
        self.protection_after_preemption = protection_after_preemption
        self.checkpoint_before_preemption = checkpoint_before_preemption
        self.preemption_history: Dict[str, List[datetime]] = {}
    
    def can_preempt(
        self,
        job: BaseJob,
        trigger: PreemptionTrigger,
        runtime: Optional[timedelta] = None,
        current_time: Optional[datetime] = None,
    ) -> Tuple[bool, Optional[str]]:
        """Determine if a job can be preempted."""
        if current_time is None:
            current_time = datetime.now()
        
        # Critical jobs cannot be preempted
        if job.priority == Priority.CRITICAL:
            return False, "Critical priority jobs cannot be preempted"
        
        # Maintenance preemption may override other restrictions
        if trigger == PreemptionTrigger.MAINTENANCE:
            # Still don't preempt critical jobs
            if job.priority == Priority.CRITICAL:
                return False, "Critical priority jobs cannot be preempted even for maintenance"
            
            # For others, maintenance can override
            return True, None
        
        # Check if it's been running long enough
        if runtime is not None and runtime < self.min_runtime_before_preemption:
            return False, f"Job has not run long enough for preemption ({runtime} < {self.min_runtime_before_preemption})"
        
        # Check preemption history
        job_id = job.id
        if job_id in self.preemption_history:
            # Check if recently preempted
            last_preemption = max(self.preemption_history[job_id])
            if current_time - last_preemption < self.protection_after_preemption:
                return False, f"Job was recently preempted and is protected ({current_time - last_preemption} < {self.protection_after_preemption})"
            
            # Check daily limit
            today = current_time.date()
            preemptions_today = sum(
                1 for ts in self.preemption_history[job_id]
                if ts.date() == today
            )
            
            max_preemptions = self.max_preemptions_per_day.get(job.priority, 0)
            if preemptions_today >= max_preemptions:
                return False, f"Job has reached maximum preemptions for today ({preemptions_today} >= {max_preemptions})"
        
        return True, None
    
    def record_preemption(self, job_id: str, time: Optional[datetime] = None) -> None:
        """Record a preemption event."""
        if time is None:
            time = datetime.now()
        
        if job_id not in self.preemption_history:
            self.preemption_history[job_id] = []
        
        self.preemption_history[job_id].append(time)
    
    def get_action_for_trigger(
        self,
        job: BaseJob,
        trigger: PreemptionTrigger,
    ) -> PreemptionAction:
        """Determine the appropriate preemption action for a trigger."""
        if trigger == PreemptionTrigger.MAINTENANCE:
            return PreemptionAction.CHECKPOINT_AND_STOP
        
        if trigger == PreemptionTrigger.HIGHER_PRIORITY:
            # Try migration first for high priority jobs
            if job.priority in [Priority.HIGH, Priority.MEDIUM]:
                return PreemptionAction.MIGRATE
            return PreemptionAction.CHECKPOINT_AND_STOP
        
        if trigger == PreemptionTrigger.RESOURCE_SHORTAGE:
            # For resource shortage, requeue lower priority jobs
            if job.priority in [Priority.LOW, Priority.BACKGROUND]:
                return PreemptionAction.REQUEUE
            return PreemptionAction.CONTINUE_LIMITED
        
        if trigger == PreemptionTrigger.FAIRNESS:
            return PreemptionAction.REQUEUE
        
        if trigger == PreemptionTrigger.ADMIN:
            return PreemptionAction.CHECKPOINT_AND_STOP
        
        if trigger == PreemptionTrigger.DEADLINE:
            return PreemptionAction.CANCEL
        
        # Default
        return PreemptionAction.CHECKPOINT_AND_STOP


class JobQueue(Generic[T]):
    """Queue for managing jobs.
    
    This queue implementation provides common functionality for both
    render farm jobs and scientific computing simulations. It supports
    multiple queue policies, priority aging, fairness adjustments,
    and comprehensive statistics tracking.
    """

    def __init__(
        self,
        policy: QueuePolicy = QueuePolicy.WEIGHTED,
        preemption_policy: Optional[PreemptionPolicy] = None,
    ):
        self.policy = policy
        self.preemption_policy = preemption_policy or PreemptionPolicy()
        self.queue: List[QueuedJob[T]] = []
        self.job_map: Dict[str, QueuedJob[T]] = {}
        self.stats = QueueStats()
        self.priority_aging_factor = 0.1  # How much to boost priority over time
        self.aging_interval = timedelta(hours=12)  # How often to apply aging
        self.user_fairness_weights: Dict[str, float] = {}  # Weights for fair sharing
        self.project_fairness_weights: Dict[str, float] = {}  # Weights for fair sharing
        self.fairness_metric = FairnessMetric.WEIGHTED
        self.last_fairness_adjustment = datetime.now()
        self.fairness_adjustment_interval = timedelta(hours=6)
    
    def enqueue(self, job: T) -> Result[bool]:
        """Add a job to the queue."""
        if job.id in self.job_map:
            return Result.err(f"Job {job.id} is already in the queue")
        
        job.status = JobStatus.QUEUED
        queued_job = QueuedJob(job, datetime.now())
        heapq.heappush(self.queue, queued_job)
        self.job_map[job.id] = queued_job
        
        self.stats.update_on_submit(job)
        
        logger.info(f"Job {job.id} added to queue with priority {job.priority}")
        return Result.ok(True)
    
    def dequeue(self) -> Optional[T]:
        """Get the highest priority job from the queue."""
        if not self.queue:
            return None
        
        # Get the highest priority job
        queued_job = heapq.heappop(self.queue)
        job = queued_job.job
        
        # Remove from job map
        del self.job_map[job.id]
        
        # Update status
        job.status = JobStatus.RUNNING
        
        # Update stats
        self.stats.update_on_start(job, queued_job.submit_time)
        
        logger.info(f"Job {job.id} dequeued with priority {job.priority}")
        return job
    
    def peek(self) -> Optional[T]:
        """Look at the highest priority job without removing it."""
        if not self.queue:
            return None
        
        return self.queue[0].job
    
    def remove(self, job_id: str) -> Result[bool]:
        """Remove a specific job from the queue."""
        if job_id not in self.job_map:
            return Result.err(f"Job {job_id} not found in queue")
        
        queued_job = self.job_map[job_id]
        self.queue.remove(queued_job)
        heapq.heapify(self.queue)  # Reestablish heap invariant
        
        del self.job_map[job_id]
        
        # Update stats
        self.stats.update_on_cancel(queued_job.job)
        
        logger.info(f"Job {job_id} removed from queue")
        return Result.ok(True)
    
    def update_job_status(self, job_id: str, status: JobStatus) -> Result[bool]:
        """Update the status of a job in the queue."""
        # Only called for jobs that are still in the queue
        if job_id not in self.job_map:
            return Result.err(f"Job {job_id} not found in queue")
        
        queued_job = self.job_map[job_id]
        old_status = queued_job.job.status
        queued_job.job.status = status
        
        logger.info(f"Job {job_id} status updated: {old_status} -> {status}")
        
        # Update stats based on status change
        if status == JobStatus.COMPLETED:
            self.stats.update_on_complete(queued_job.job)
        elif status == JobStatus.FAILED:
            self.stats.update_on_fail(queued_job.job)
        elif status == JobStatus.CANCELLED:
            self.stats.update_on_cancel(queued_job.job)
        
        # If job is now running, we need to dequeue it
        if status == JobStatus.RUNNING:
            return self.remove(job_id)
        
        return Result.ok(True)
    
    def update_priority(self, job_id: str, new_priority: Priority) -> Result[bool]:
        """Update the priority of a queued job."""
        if job_id not in self.job_map:
            return Result.err(f"Job {job_id} not found in queue")
        
        queued_job = self.job_map[job_id]
        old_priority = queued_job.job.priority
        
        if old_priority == new_priority:
            return Result.ok(True)  # No change needed
        
        # Update priority
        queued_job.update_priority(new_priority)
        
        # Reheapify the queue
        heapq.heapify(self.queue)
        
        logger.info(f"Job {job_id} priority updated: {old_priority} -> {new_priority}")
        return Result.ok(True)
    
    def get_position(self, job_id: str) -> Optional[int]:
        """Get the position of a job in the queue."""
        if job_id not in self.job_map:
            return None
        
        queued_job = self.job_map[job_id]
        return self.queue.index(queued_job) + 1  # 1-based position
    
    def get_queued_jobs(self) -> List[T]:
        """Get all jobs currently in the queue."""
        return [queued_job.job for queued_job in self.queue]
    
    def apply_aging(self) -> None:
        """Apply priority aging to long-waiting jobs."""
        now = datetime.now()
        
        for queued_job in self.queue:
            # Skip jobs that had priority updates recently
            last_update = queued_job.priority_updates[-1][0]
            if now - last_update < self.aging_interval:
                continue
            
            # Skip jobs with highest priority already
            if queued_job.job.priority == Priority.CRITICAL:
                continue
            
            # Calculate aging factor based on wait time
            wait_time = now - queued_job.submit_time
            aging_periods = wait_time / self.aging_interval
            
            # Only apply aging if waited for at least one period
            if aging_periods >= 1:
                # Calculate if priority should be boosted
                priority_values = list(Priority)
                current_index = priority_values.index(queued_job.job.priority)
                
                # Potentially move to next higher priority (lower index)
                if current_index > 0:  # Not already at highest
                    # Probability of promotion increases with wait time
                    promotion_probability = min(1.0, self.priority_aging_factor * aging_periods)
                    
                    # Simple deterministic approach for this implementation
                    if promotion_probability >= 0.5:
                        new_priority = priority_values[current_index - 1]
                        self.update_priority(queued_job.job.id, new_priority)
                        logger.info(
                            f"Priority aged for long-waiting job {queued_job.job.id}: "
                            f"{queued_job.job.priority} -> {new_priority}"
                        )
    
    def apply_fairness_adjustments(self) -> None:
        """Apply fairness adjustments to the queue."""
        now = datetime.now()
        
        # Only apply fairness adjustments periodically
        if now - self.last_fairness_adjustment < self.fairness_adjustment_interval:
            return
        
        self.last_fairness_adjustment = now
        
        # Skip if queue is small
        if len(self.queue) < 2:
            return
        
        # Get resource usage by user and project
        user_usage: Dict[str, float] = {}
        project_usage: Dict[str, float] = {}
        
        for queued_job in self.queue:
            user = queued_job.job.owner
            project = queued_job.job.project
            
            # For now, just count jobs
            user_usage[user] = user_usage.get(user, 0) + 1
            project_usage[project] = project_usage.get(project, 0) + 1
        
        # Calculate fair shares
        total_jobs = len(self.queue)
        
        for queued_job in self.queue:
            user = queued_job.job.owner
            project = queued_job.job.project
            
            # Skip critical jobs
            if queued_job.job.priority == Priority.CRITICAL:
                continue
            
            user_share = user_usage.get(user, 0) / total_jobs
            project_share = project_usage.get(project, 0) / total_jobs
            
            user_weight = self.user_fairness_weights.get(user, 1.0)
            project_weight = self.project_fairness_weights.get(project, 1.0)
            
            # If user or project is using more than their fair share, lower priority
            fair_share_threshold = 0.5  # Arbitrary threshold
            
            if (user_share > fair_share_threshold / user_weight or
                project_share > fair_share_threshold / project_weight):
                
                # Only lower priority if not already at lowest
                if queued_job.job.priority != Priority.BACKGROUND:
                    # Find the next lower priority
                    priority_values = list(Priority)
                    current_index = priority_values.index(queued_job.job.priority)
                    
                    if current_index < len(priority_values) - 1:
                        new_priority = priority_values[current_index + 1]
                        self.update_priority(queued_job.job.id, new_priority)
                        logger.info(
                            f"Priority lowered for fairness: {queued_job.job.id} "
                            f"({queued_job.job.priority} -> {new_priority})"
                        )
        
        # Reheapify the queue after all adjustments
        heapq.heapify(self.queue)
    
    def get_stats(self) -> QueueStats:
        """Get current queue statistics."""
        return self.stats
    
    def get_wait_time_estimate(self, job: T) -> timedelta:
        """Estimate wait time for a new job."""
        # This is a simple estimation that considers the current queue state
        # A more sophisticated implementation would use historical data and resource availability
        
        base_wait_time = timedelta(minutes=30)
        
        # Adjust based on priority
        priority_factor = {
            Priority.CRITICAL: 0.2,
            Priority.HIGH: 0.5,
            Priority.MEDIUM: 1.0,
            Priority.LOW: 2.0,
            Priority.BACKGROUND: 4.0,
        }.get(job.priority, 1.0)
        
        # Adjust based on queue length
        queue_factor = max(1.0, len(self.queue) / 10)
        
        return base_wait_time * priority_factor * queue_factor