"""
Job scheduler for the unified concurrent task scheduler.

This module provides a common job scheduler implementation that can be used by both
the render farm manager and scientific computing implementations.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Generic, TypeVar, Any

from common.core.interfaces import SchedulerInterface
from common.core.models import (
    AuditLogEntry,
    BaseJob,
    BaseNode,
    JobStatus,
    Priority,
    Result,
)
from common.job_management.queue import JobQueue, QueuePolicy, PreemptionTrigger

logger = logging.getLogger(__name__)

# Type variables for job and node types
T = TypeVar("T", bound=BaseJob)
N = TypeVar("N", bound=BaseNode)


class JobScheduler(Generic[T, N], SchedulerInterface):
    """
    Job scheduler for managing compute resources and scheduling jobs.
    
    This implementation provides a common scheduler that works with both
    render jobs and scientific computing simulations. It handles prioritization,
    resource allocation, and deadline-based scheduling.
    """
    
    def __init__(
        self,
        queue: Optional[JobQueue[T]] = None,
        deadline_safety_margin_hours: float = 2.0,
        enable_preemption: bool = True,
    ):
        """
        Initialize the job scheduler.
        
        Args:
            queue: The job queue to use (will create if not provided)
            deadline_safety_margin_hours: Safety margin to add to estimated job duration
            enable_preemption: Whether to enable job preemption
        """
        self.queue = queue or JobQueue[T](policy=QueuePolicy.WEIGHTED)
        self.deadline_safety_margin_hours = deadline_safety_margin_hours
        self.enable_preemption = enable_preemption
        self.logger = logging.getLogger("scheduler")
        self._effective_priorities: Dict[str, Priority] = {}
    
    def schedule_jobs(self, jobs: List[T], nodes: List[N]) -> Dict[str, str]:
        """
        Schedule jobs to nodes based on priority, deadlines, and resource requirements.
        
        Args:
            jobs: List of jobs to schedule
            nodes: List of available nodes
            
        Returns:
            Dictionary mapping job IDs to node IDs
        """
        # Filter out only jobs that are ready to be scheduled
        eligible_jobs = self._get_eligible_jobs(jobs)
        
        # Update job priorities based on deadlines and dependencies
        eligible_jobs = self.update_priorities(eligible_jobs)
        
        # Get available nodes (not running jobs or in maintenance)
        available_nodes = [
            node for node in nodes 
            if node.status == "online" and not node.assigned_jobs
        ]
        
        # Get nodes running preemptible jobs (if preemption is enabled)
        preemptible_nodes = []
        if self.enable_preemption:
            running_job_map = {}
            for job in jobs:
                if job.status == JobStatus.RUNNING and job.assigned_node_id:
                    running_job_map[job.id] = job
            
            preemptible_nodes = [
                node for node in nodes
                if node.status == "online" 
                and node.assigned_jobs
                and any(
                    job_id in running_job_map for job_id in node.assigned_jobs
                )
            ]
        
        # Map of job ID to node ID for scheduled jobs
        scheduled_jobs: Dict[str, str] = {}
        
        # Schedule jobs based on priority and deadline
        for job in eligible_jobs:
            # First, try to find a suitable available node
            assigned_node = self._find_suitable_node(job, available_nodes)
            
            if assigned_node:
                self.logger.info(f"Scheduling job {job.id} on node {assigned_node.id}")
                scheduled_jobs[job.id] = assigned_node.id
                
                # Update node's assignment status
                assigned_node.assigned_jobs.append(job.id)
                
                # Remove node from available list
                available_nodes = [node for node in available_nodes if node.id != assigned_node.id]
                continue
            
            # If no available node and preemption is enabled, try to preempt a lower-priority job
            if self.enable_preemption and preemptible_nodes:
                for node in preemptible_nodes:
                    # Check if any job on this node can be preempted
                    for job_id in node.assigned_jobs:
                        if job_id in running_job_map:
                            running_job = running_job_map[job_id]
                            
                            if self.should_preempt(running_job, job):
                                scheduled_jobs[job.id] = node.id
                                self.logger.info(
                                    f"Job {job.id} preempting job {running_job.id} on node {node.id}"
                                )
                                
                                # Remove node from preemptible list
                                preemptible_nodes = [n for n in preemptible_nodes if n.id != node.id]
                                break
                    
                    # If job has been scheduled, break out of node loop
                    if job.id in scheduled_jobs:
                        break
        
        return scheduled_jobs
    
    def update_priorities(self, jobs: List[T]) -> List[T]:
        """
        Update job priorities based on deadlines and completion status.
        
        Args:
            jobs: List of jobs
            
        Returns:
            List of updated jobs with adjusted priorities
        """
        now = datetime.now()
        updated_jobs = []
        
        # Create a mapping of job IDs to jobs for faster lookups
        jobs_by_id = {job.id: job for job in jobs}
        
        # Initialize effective priorities dictionary if not already
        if not hasattr(self, '_effective_priorities'):
            self._effective_priorities = {}
        
        for job in jobs:
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                updated_jobs.append(job)
                continue
            
            original_priority = job.priority
            
            # Apply deadline-based priority adjustments if job has deadline attribute
            if hasattr(job, 'deadline'):
                time_until_deadline = (job.deadline - now).total_seconds()
                estimated_time_needed = 0
                
                # Calculate estimated time needed
                if hasattr(job, 'estimated_duration'):
                    estimated_time_needed = job.estimated_duration.total_seconds() * (1 - job.progress / 100)
                elif hasattr(job, 'estimated_duration_hours'):
                    estimated_time_needed = job.estimated_duration_hours * 3600 * (1 - job.progress / 100)
                
                # Add safety margin to the estimated time
                estimated_time_with_margin = estimated_time_needed + (self.deadline_safety_margin_hours * 3600)
                
                # Adjust priority based on deadline proximity
                if estimated_time_with_margin >= time_until_deadline:
                    # Job won't complete before deadline with current priority
                    if job.priority == Priority.HIGH:
                        job.priority = Priority.CRITICAL
                    elif job.priority == Priority.MEDIUM:
                        job.priority = Priority.HIGH
                    elif job.priority == Priority.LOW:
                        job.priority = Priority.MEDIUM
                elif time_until_deadline < 24 * 3600:  # Less than 24 hours until deadline
                    if job.priority == Priority.MEDIUM:
                        job.priority = Priority.HIGH
                    elif job.priority == Priority.LOW:
                        job.priority = Priority.MEDIUM
                elif time_until_deadline < 48 * 3600:  # Less than 48 hours until deadline
                    if job.priority == Priority.LOW:
                        job.priority = Priority.MEDIUM
            
            # Apply priority inheritance - child jobs inherit the highest priority of their parents
            if hasattr(job, 'dependencies') and job.dependencies:
                # Find highest priority among parent jobs
                parent_priorities = []
                for dep_id in job.dependencies:
                    if dep_id in jobs_by_id:
                        parent_job = jobs_by_id[dep_id]
                        parent_priorities.append(parent_job.priority)
                
                if parent_priorities:
                    # Sort parent priorities by their enum order (CRITICAL is highest)
                    sorted_priorities = sorted(
                        parent_priorities, 
                        key=lambda p: [
                            Priority.CRITICAL, Priority.HIGH, Priority.MEDIUM, 
                            Priority.LOW, Priority.BACKGROUND
                        ].index(p)
                    )
                    highest_parent_priority = sorted_priorities[0]
                    
                    # If parent has higher priority than child, child inherits parent's priority
                    if self._get_priority_value(highest_parent_priority) > self._get_priority_value(job.priority):
                        # Store in dictionary rather than as an attribute
                        self._effective_priorities[job.id] = highest_parent_priority
                        self.logger.info(f"Job {job.id} inherited priority {highest_parent_priority} from parent")
            
            updated_jobs.append(job)
        
        return updated_jobs
    
    def can_meet_deadline(self, job: T, available_nodes: List[N]) -> bool:
        """
        Determine if a job's deadline can be met with available resources.
        
        Args:
            job: The job to evaluate
            available_nodes: List of available nodes
            
        Returns:
            True if the deadline can be met, False otherwise
        """
        # If job does not have a deadline, assume it can be met
        if not hasattr(job, 'deadline'):
            return True
        
        now = datetime.now()
        time_until_deadline = (job.deadline - now).total_seconds() / 3600  # in hours
        
        # Calculate estimated duration
        if hasattr(job, 'estimated_duration'):
            estimated_duration = job.estimated_duration.total_seconds() / 3600 * (1 - job.progress / 100)
        elif hasattr(job, 'estimated_duration_hours'):
            estimated_duration = job.estimated_duration_hours * (1 - job.progress / 100)
        else:
            # If no duration information, assume it can be met
            return True
        
        # Add safety margin
        estimated_duration_with_margin = estimated_duration + self.deadline_safety_margin_hours
        
        # Check if there's enough time to complete the job before the deadline
        if estimated_duration_with_margin > time_until_deadline:
            return False
        
        # Check if there are suitable nodes to run the job
        suitable_node = self._find_suitable_node(job, available_nodes)
        return suitable_node is not None
    
    def should_preempt(self, running_job: T, pending_job: T) -> bool:
        """
        Determine if a running job should be preempted for a pending job.
        
        Args:
            running_job: The currently running job
            pending_job: The job that might preempt the running job
            
        Returns:
            True if the running job should be preempted, False otherwise
        """
        # Cannot preempt if the running job has a special attribute indicating it cannot be preempted
        if hasattr(running_job, 'can_be_preempted') and not running_job.can_be_preempted:
            return False
        
        # Critical jobs can preempt lower priority jobs
        if pending_job.priority == Priority.CRITICAL and running_job.priority != Priority.CRITICAL:
            return True
        
        # Check for effective priority of pending job
        pending_priority = self._effective_priorities.get(pending_job.id, pending_job.priority)
        
        # If both jobs have deadlines, check deadline urgency
        if hasattr(pending_job, 'deadline') and hasattr(running_job, 'deadline'):
            now = datetime.now()
            
            # Calculate time until deadline
            pending_deadline_time = (pending_job.deadline - now).total_seconds() / 3600  # in hours
            running_deadline_time = (running_job.deadline - now).total_seconds() / 3600  # in hours
            
            # Calculate estimated completion time
            if hasattr(pending_job, 'estimated_duration_hours'):
                pending_estimated_time = pending_job.estimated_duration_hours * (1 - pending_job.progress / 100)
            elif hasattr(pending_job, 'estimated_duration'):
                pending_estimated_time = pending_job.estimated_duration.total_seconds() / 3600 * (1 - pending_job.progress / 100)
            else:
                pending_estimated_time = 0
                
            if hasattr(running_job, 'estimated_duration_hours'):
                running_estimated_time = running_job.estimated_duration_hours * (1 - running_job.progress / 100)
            elif hasattr(running_job, 'estimated_duration'):
                running_estimated_time = running_job.estimated_duration.total_seconds() / 3600 * (1 - running_job.progress / 100)
            else:
                running_estimated_time = 0
            
            # Pending job will miss deadline but running job won't
            pending_will_miss = pending_estimated_time + self.deadline_safety_margin_hours > pending_deadline_time
            running_will_complete = running_estimated_time + self.deadline_safety_margin_hours < running_deadline_time
            
            # Preempt if pending job has higher priority and is in danger of missing deadline
            if (self._get_priority_value(pending_priority) > self._get_priority_value(running_job.priority) 
                    and pending_will_miss and running_will_complete):
                return True
        
        # In non-deadline case, only preempt if pending job has higher priority
        return self._get_priority_value(pending_priority) > self._get_priority_value(running_job.priority)
    
    def _get_eligible_jobs(self, jobs: List[T]) -> List[T]:
        """
        Filter jobs to get only those eligible for scheduling.
        
        Args:
            jobs: List of all jobs
            
        Returns:
            List of jobs eligible for scheduling
        """
        eligible_jobs = []
        jobs_by_id = {job.id: job for job in jobs}
        
        for job in jobs:
            # Only consider pending or queued jobs
            if job.status not in [JobStatus.PENDING, JobStatus.QUEUED]:
                continue
            
            # Skip failed jobs
            if job.status == JobStatus.FAILED:
                continue
            
            # Check dependencies - only include jobs with satisfied dependencies
            if hasattr(job, 'dependencies') and job.dependencies:
                all_deps_satisfied = True
                
                for dep_id in job.dependencies:
                    # Look up the dependency job
                    dep_job = jobs_by_id.get(dep_id)
                    
                    # If dependency not found, consider it complete for compatibility
                    if dep_job is None:
                        continue
                    
                    # Check if dependency is satisfied based on its status or progress
                    dep_satisfied = False
                    
                    # Dependency is satisfied if completed
                    if dep_job.status == JobStatus.COMPLETED:
                        dep_satisfied = True
                    # Partial dependency satisfaction based on progress
                    elif dep_job.status == JobStatus.RUNNING and dep_job.progress >= 50.0:
                        dep_satisfied = True
                    
                    if not dep_satisfied:
                        all_deps_satisfied = False
                        break
                
                if not all_deps_satisfied:
                    continue
            
            # If we get here, the job is eligible for scheduling
            eligible_jobs.append(job)
        
        return eligible_jobs
    
    def _find_suitable_node(self, job: T, nodes: List[N]) -> Optional[N]:
        """
        Find a suitable node for a job based on resource requirements.
        
        Args:
            job: The job to place
            nodes: List of available nodes
            
        Returns:
            A suitable node or None if no suitable node is found
        """
        suitable_nodes = []
        
        for node in nodes:
            # Check if node can accommodate job's resource requirements
            if not node.can_accommodate(job.resource_requirements):
                continue
                
            suitable_nodes.append(node)
        
        if not suitable_nodes:
            return None
        
        # Sort suitable nodes by power efficiency if available
        if hasattr(suitable_nodes[0], 'power_efficiency_rating'):
            suitable_nodes.sort(key=lambda n: n.power_efficiency_rating, reverse=True)
        
        return suitable_nodes[0]
    
    def _get_priority_value(self, priority: Priority) -> int:
        """
        Get a numeric value for a job priority for sorting purposes.
        
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