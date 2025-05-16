"""
Priority management for the unified concurrent task scheduler.

This module provides priority management functionality for both render farm
and scientific computing jobs, including priority inheritance, deadline-based
priority adjustments, and fairness mechanisms.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Generic, TypeVar, Any

from common.core.models import (
    BaseJob,
    JobStatus,
    Priority,
    Result,
)

logger = logging.getLogger(__name__)

# Type variable for job types
T = TypeVar("T", bound=BaseJob)


class PriorityPolicy(str, Enum):
    """Policies for managing job priorities."""
    
    STATIC = "static"  # Static priorities set by users
    DEADLINE = "deadline"  # Priority adjustments based on deadlines
    INHERITANCE = "inheritance"  # Priority inheritance from parent jobs
    AGING = "aging"  # Priority aging for waiting jobs
    FAIRNESS = "fairness"  # Fairness adjustments
    WEIGHTED = "weighted"  # Weighted combination of multiple policies


class PriorityInheritanceMode(str, Enum):
    """Modes for priority inheritance between jobs."""
    
    NONE = "none"  # No inheritance
    PARENTS_TO_CHILDREN = "parents_to_children"  # Parents influence children
    CHILDREN_TO_PARENTS = "children_to_parents"  # Children influence parents
    BIDIRECTIONAL = "bidirectional"  # Both directions


class PriorityManager(Generic[T]):
    """
    Manages job priorities for both render farm and scientific computing jobs.
    
    This implementation provides common priority management mechanisms including
    deadline-based adjustments, priority inheritance, aging, and fairness
    considerations.
    """
    
    def __init__(
        self,
        policy: PriorityPolicy = PriorityPolicy.WEIGHTED,
        priority_inheritance_mode: PriorityInheritanceMode = PriorityInheritanceMode.PARENTS_TO_CHILDREN,
        aging_interval: timedelta = timedelta(hours=12),
        aging_factor: float = 0.1,
        deadline_safety_margin_hours: float = 2.0,
        fairness_adjustment_interval: timedelta = timedelta(hours=6),
    ):
        """
        Initialize the priority manager.
        
        Args:
            policy: Priority policy to use
            priority_inheritance_mode: How priority inheritance should work
            aging_interval: How often to apply priority aging
            aging_factor: Factor for priority aging calculations
            deadline_safety_margin_hours: Safety margin for deadline calculations
            fairness_adjustment_interval: How often to apply fairness adjustments
        """
        self.policy = policy
        self.priority_inheritance_mode = priority_inheritance_mode
        self.aging_interval = aging_interval
        self.aging_factor = aging_factor
        self.deadline_safety_margin_hours = deadline_safety_margin_hours
        self.fairness_adjustment_interval = fairness_adjustment_interval
        self.effective_priorities: Dict[str, Priority] = {}
        self.priority_updates: Dict[str, List[Tuple[datetime, Priority]]] = {}
        self.last_aging_adjustment = datetime.now()
        self.last_fairness_adjustment = datetime.now()
        self.user_fairness_weights: Dict[str, float] = {}
        self.project_fairness_weights: Dict[str, float] = {}
        self.logger = logging.getLogger("priority_manager")
    
    def update_priorities(self, jobs: List[T]) -> List[T]:
        """
        Update job priorities based on the current policy.
        
        Args:
            jobs: List of jobs to update
            
        Returns:
            List of updated jobs
        """
        # Apply appropriate priority adjustments based on policy
        if self.policy == PriorityPolicy.STATIC:
            # No changes with static policy
            return jobs
        
        if self.policy in [PriorityPolicy.DEADLINE, PriorityPolicy.WEIGHTED]:
            jobs = self._apply_deadline_based_adjustments(jobs)
        
        if self.policy in [PriorityPolicy.INHERITANCE, PriorityPolicy.WEIGHTED]:
            jobs = self._apply_priority_inheritance(jobs)
        
        if self.policy in [PriorityPolicy.AGING, PriorityPolicy.WEIGHTED]:
            jobs = self._apply_priority_aging(jobs)
        
        if self.policy in [PriorityPolicy.FAIRNESS, PriorityPolicy.WEIGHTED]:
            jobs = self._apply_fairness_adjustments(jobs)
        
        return jobs
    
    def set_priority(self, job: T, priority: Priority) -> Result[bool]:
        """
        Set a job's priority.
        
        Args:
            job: The job to update
            priority: The new priority
            
        Returns:
            Result indicating success or failure
        """
        if job.priority == priority:
            return Result.ok(True)
        
        old_priority = job.priority
        job.priority = priority
        
        # Record the update
        job_id = job.id
        if job_id not in self.priority_updates:
            self.priority_updates[job_id] = []
        
        self.priority_updates[job_id].append((datetime.now(), priority))
        
        self.logger.info(f"Job {job_id} priority updated: {old_priority} -> {priority}")
        return Result.ok(True)
    
    def get_effective_priority(self, job: T) -> Priority:
        """
        Get the effective priority of a job, accounting for inheritance.
        
        Args:
            job: The job to evaluate
            
        Returns:
            The effective priority
        """
        if job.id in self.effective_priorities:
            return self.effective_priorities[job.id]
        
        return job.priority
    
    def _apply_deadline_based_adjustments(self, jobs: List[T]) -> List[T]:
        """
        Apply deadline-based priority adjustments.
        
        Args:
            jobs: List of jobs to update
            
        Returns:
            List of updated jobs
        """
        now = datetime.now()
        updated_jobs = []
        
        for job in jobs:
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                updated_jobs.append(job)
                continue
            
            # Skip if job doesn't have deadline attribute
            if not hasattr(job, 'deadline'):
                updated_jobs.append(job)
                continue
            
            time_until_deadline = (job.deadline - now).total_seconds()
            
            # Get estimated duration in seconds
            if hasattr(job, 'estimated_duration'):
                estimated_time_needed = job.estimated_duration.total_seconds() * (1 - job.progress / 100)
            elif hasattr(job, 'estimated_duration_hours'):
                estimated_time_needed = job.estimated_duration_hours * 3600 * (1 - job.progress / 100)
            else:
                # Skip if we can't determine duration
                updated_jobs.append(job)
                continue
            
            # Add safety margin to the estimated time
            estimated_time_with_margin = estimated_time_needed + (self.deadline_safety_margin_hours * 3600)
            
            # Current priority
            old_priority = job.priority
            
            # Adjust priority based on deadline proximity
            if estimated_time_with_margin >= time_until_deadline:
                # Job won't complete before deadline with current priority
                if job.priority == Priority.HIGH:
                    self.set_priority(job, Priority.CRITICAL)
                elif job.priority == Priority.MEDIUM:
                    self.set_priority(job, Priority.HIGH)
                elif job.priority == Priority.LOW:
                    self.set_priority(job, Priority.MEDIUM)
                elif job.priority == Priority.BACKGROUND:
                    self.set_priority(job, Priority.LOW)
            elif time_until_deadline < 24 * 3600:  # Less than 24 hours until deadline
                # Shorter-term deadline adjustment
                if job.priority == Priority.MEDIUM:
                    self.set_priority(job, Priority.HIGH)
                elif job.priority == Priority.LOW:
                    self.set_priority(job, Priority.MEDIUM)
                elif job.priority == Priority.BACKGROUND:
                    self.set_priority(job, Priority.LOW)
            elif time_until_deadline < 48 * 3600:  # Less than 48 hours until deadline
                # Longer-term deadline adjustment
                if job.priority == Priority.LOW:
                    self.set_priority(job, Priority.MEDIUM)
                elif job.priority == Priority.BACKGROUND:
                    self.set_priority(job, Priority.LOW)
            
            updated_jobs.append(job)
        
        return updated_jobs
    
    def _apply_priority_inheritance(self, jobs: List[T]) -> List[T]:
        """
        Apply priority inheritance between related jobs.
        
        Args:
            jobs: List of jobs to update
            
        Returns:
            List of updated jobs
        """
        updated_jobs = []
        
        # Create a mapping of job IDs to jobs for faster lookups
        jobs_by_id = {job.id: job for job in jobs}
        
        # Reset effective priorities for this run
        self.effective_priorities = {}
        
        for job in jobs:
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                updated_jobs.append(job)
                continue
            
            # Apply parent-to-child inheritance
            if self.priority_inheritance_mode in [PriorityInheritanceMode.PARENTS_TO_CHILDREN, 
                                                PriorityInheritanceMode.BIDIRECTIONAL]:
                if hasattr(job, 'dependencies') and job.dependencies:
                    # Find highest priority among parent jobs
                    parent_priorities = []
                    for dep_id in job.dependencies:
                        if dep_id in jobs_by_id:
                            parent_job = jobs_by_id[dep_id]
                            # Use parent's effective priority if available
                            parent_priority = self.get_effective_priority(parent_job)
                            parent_priorities.append(parent_priority)
                    
                    if parent_priorities:
                        # Sort parent priorities by enum value
                        parent_priorities.sort(key=self._get_priority_value, reverse=True)
                        highest_parent_priority = parent_priorities[0]
                        
                        # If parent has higher priority than child, child inherits parent's priority
                        if self._get_priority_value(highest_parent_priority) > self._get_priority_value(job.priority):
                            self.effective_priorities[job.id] = highest_parent_priority
                            self.logger.info(
                                f"Job {job.id} inherited priority {highest_parent_priority} from parent"
                            )
            
            # Apply child-to-parent inheritance
            if self.priority_inheritance_mode in [PriorityInheritanceMode.CHILDREN_TO_PARENTS, 
                                                PriorityInheritanceMode.BIDIRECTIONAL]:
                # Find all jobs where this job is a dependency
                children = []
                for potential_child in jobs:
                    if (hasattr(potential_child, 'dependencies') 
                            and job.id in potential_child.dependencies):
                        children.append(potential_child)
                
                if children:
                    # Find highest priority among children
                    child_priorities = [self.get_effective_priority(child) for child in children]
                    child_priorities.sort(key=self._get_priority_value, reverse=True)
                    highest_child_priority = child_priorities[0]
                    
                    # If child has higher priority than parent, parent inherits child's priority
                    if self._get_priority_value(highest_child_priority) > self._get_priority_value(job.priority):
                        self.effective_priorities[job.id] = highest_child_priority
                        self.logger.info(
                            f"Job {job.id} inherited priority {highest_child_priority} from child"
                        )
            
            updated_jobs.append(job)
        
        return updated_jobs
    
    def _apply_priority_aging(self, jobs: List[T]) -> List[T]:
        """
        Apply priority aging to long-waiting jobs.
        
        Args:
            jobs: List of jobs to update
            
        Returns:
            List of updated jobs
        """
        now = datetime.now()
        
        # Only apply aging periodically
        if now - self.last_aging_adjustment < self.aging_interval:
            return jobs
        
        self.last_aging_adjustment = now
        updated_jobs = []
        
        for job in jobs:
            if job.status not in [JobStatus.PENDING, JobStatus.QUEUED]:
                updated_jobs.append(job)
                continue
            
            # Skip already critical jobs
            if job.priority == Priority.CRITICAL:
                updated_jobs.append(job)
                continue
            
            # Check if job was recently updated
            recently_updated = False
            if job.id in self.priority_updates:
                last_update = self.priority_updates[job.id][-1][0]
                if now - last_update < self.aging_interval:
                    recently_updated = True
            
            if recently_updated:
                updated_jobs.append(job)
                continue
            
            # Calculate wait time
            wait_time = now - job.submission_time
            aging_periods = wait_time / self.aging_interval
            
            # Only apply aging if waited for at least one period
            if aging_periods >= 1:
                # Priority values in order
                priority_values = [Priority.CRITICAL, Priority.HIGH, Priority.MEDIUM, Priority.LOW, Priority.BACKGROUND]
                current_index = priority_values.index(job.priority)
                
                # Potentially move to next higher priority (lower index)
                if current_index > 0:  # Not already at highest
                    # Probability of promotion increases with wait time
                    promotion_probability = min(1.0, self.aging_factor * aging_periods)
                    
                    # Simple deterministic approach
                    if promotion_probability >= 0.5:
                        new_priority = priority_values[current_index - 1]
                        self.set_priority(job, new_priority)
                        self.logger.info(
                            f"Priority aged for long-waiting job {job.id}: "
                            f"{job.priority} -> {new_priority}"
                        )
            
            updated_jobs.append(job)
        
        return updated_jobs
    
    def _apply_fairness_adjustments(self, jobs: List[T]) -> List[T]:
        """
        Apply fairness adjustments to ensure fair resource distribution.
        
        Args:
            jobs: List of jobs to update
            
        Returns:
            List of updated jobs
        """
        now = datetime.now()
        
        # Only apply fairness adjustments periodically
        if now - self.last_fairness_adjustment < self.fairness_adjustment_interval:
            return jobs
        
        self.last_fairness_adjustment = now
        updated_jobs = []
        
        # Count jobs by user and project
        user_counts: Dict[str, int] = {}
        project_counts: Dict[str, int] = {}
        
        # Count only pending and queued jobs for fairness calculations
        pending_jobs = [job for job in jobs if job.status in [JobStatus.PENDING, JobStatus.QUEUED]]
        
        for job in pending_jobs:
            user = job.owner
            user_counts[user] = user_counts.get(user, 0) + 1
            
            project = job.project
            project_counts[project] = project_counts.get(project, 0) + 1
        
        # Calculate fair shares
        total_pending_jobs = len(pending_jobs)
        if total_pending_jobs < 2:
            return jobs  # Not enough jobs to apply fairness
            
        for job in jobs:
            if job.status not in [JobStatus.PENDING, JobStatus.QUEUED]:
                updated_jobs.append(job)
                continue
            
            # Skip critical jobs
            if job.priority == Priority.CRITICAL:
                updated_jobs.append(job)
                continue
            
            user = job.owner
            project = job.project
            
            user_share = user_counts.get(user, 0) / total_pending_jobs
            project_share = project_counts.get(project, 0) / total_pending_jobs
            
            user_weight = self.user_fairness_weights.get(user, 1.0)
            project_weight = self.project_fairness_weights.get(project, 1.0)
            
            # If user or project is using more than their fair share, lower priority
            # This is a simple fairness mechanism - more sophisticated ones could be implemented
            fair_share_threshold = 0.5  # Arbitrary threshold
            
            if (user_share > fair_share_threshold / user_weight or
                project_share > fair_share_threshold / project_weight):
                
                # Only lower priority if not already at lowest
                if job.priority != Priority.BACKGROUND:
                    # Find the next lower priority
                    priority_values = [Priority.CRITICAL, Priority.HIGH, Priority.MEDIUM, Priority.LOW, Priority.BACKGROUND]
                    current_index = priority_values.index(job.priority)
                    
                    if current_index < len(priority_values) - 1:
                        new_priority = priority_values[current_index + 1]
                        self.set_priority(job, new_priority)
                        self.logger.info(
                            f"Priority lowered for fairness: {job.id} "
                            f"({job.priority} -> {new_priority})"
                        )
            
            updated_jobs.append(job)
        
        return updated_jobs
    
    def _get_priority_value(self, priority: Priority) -> int:
        """
        Get a numeric value for a job priority for comparison.
        
        Args:
            priority: The job priority
            
        Returns:
            Numeric priority value (higher is more important)
        """
        priority_values = {
            Priority.CRITICAL: 4,
            Priority.HIGH: 3,
            Priority.MEDIUM: 2,
            Priority.LOW: 1,
            Priority.BACKGROUND: 0,
        }
        
        return priority_values.get(priority, 0)