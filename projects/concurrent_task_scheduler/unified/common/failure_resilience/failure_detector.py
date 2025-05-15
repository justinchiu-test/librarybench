"""
Failure detection for the unified concurrent task scheduler.

This module provides functionality for detecting failures in jobs, nodes, and resources
that can be used by both the render farm manager and scientific computing implementations.
"""

import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any, Union, Callable

from common.core.models import (
    BaseJob,
    BaseNode,
    JobStatus,
    NodeStatus,
    LogLevel,
    Result,
)

logger = logging.getLogger(__name__)


class FailureType(str, Enum):
    """Types of failures that can be detected."""
    
    NODE_OFFLINE = "node_offline"
    NODE_TIMEOUT = "node_timeout"
    JOB_TIMEOUT = "job_timeout"
    JOB_ERROR = "job_error"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DATA_CORRUPTION = "data_corruption"
    DEPENDENCY_FAILURE = "dependency_failure"
    NETWORK_FAILURE = "network_failure"
    SYSTEM_FAILURE = "system_failure"


class FailureLevel(str, Enum):
    """Severity levels for failures."""
    
    WARNING = "warning"  # Potential issue, not yet a failure
    ERROR = "error"  # Failure that can be handled automatically
    CRITICAL = "critical"  # Severe failure requiring manual intervention


class FailureEvent:
    """An event representing a detected failure."""
    
    def __init__(
        self,
        failure_id: str,
        failure_type: FailureType,
        level: FailureLevel,
        node_id: Optional[str] = None,
        job_id: Optional[str] = None,
        description: str = "",
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ):
        """
        Initialize a failure event.
        
        Args:
            failure_id: Unique identifier for the failure
            failure_type: Type of failure
            level: Severity level
            node_id: Optional ID of the affected node
            job_id: Optional ID of the affected job
            description: Human-readable description of the failure
            details: Additional details about the failure
            timestamp: Time when the failure was detected
        """
        self.id = failure_id
        self.failure_type = failure_type
        self.level = level
        self.node_id = node_id
        self.job_id = job_id
        self.description = description
        self.details = details or {}
        self.timestamp = timestamp or datetime.now()
        self.resolved = False
        self.resolution_time: Optional[datetime] = None
        self.resolution_description: Optional[str] = None
        
    def resolve(self, description: str = "Automatically resolved") -> None:
        """
        Mark this failure as resolved.
        
        Args:
            description: Description of how the failure was resolved
        """
        self.resolved = True
        self.resolution_time = datetime.now()
        self.resolution_description = description
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "failure_type": self.failure_type.value,
            "level": self.level.value,
            "node_id": self.node_id,
            "job_id": self.job_id,
            "description": self.description,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved,
            "resolution_time": self.resolution_time.isoformat() if self.resolution_time else None,
            "resolution_description": self.resolution_description,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FailureEvent":
        """Create from dictionary."""
        timestamp = None
        if "timestamp" in data:
            try:
                timestamp = datetime.fromisoformat(data["timestamp"])
            except ValueError:
                pass
        
        event = cls(
            failure_id=data["id"],
            failure_type=FailureType(data["failure_type"]),
            level=FailureLevel(data["level"]),
            node_id=data.get("node_id"),
            job_id=data.get("job_id"),
            description=data.get("description", ""),
            details=data.get("details", {}),
            timestamp=timestamp,
        )
        
        # Set resolution information
        event.resolved = data.get("resolved", False)
        
        if "resolution_time" in data and data["resolution_time"]:
            try:
                event.resolution_time = datetime.fromisoformat(data["resolution_time"])
            except ValueError:
                pass
        
        event.resolution_description = data.get("resolution_description")
        
        return event


class FailureDetector:
    """
    Detector for job, node, and resource failures.
    
    This class is responsible for:
    1. Monitoring job and node status
    2. Detecting failures based on defined criteria
    3. Generating failure events
    4. Tracking failure history
    """
    
    def __init__(self):
        """Initialize the failure detector."""
        self.failure_history: List[FailureEvent] = []
        self.active_failures: Dict[str, FailureEvent] = {}
        self.heartbeat_timestamps: Dict[str, datetime] = {}
        self.last_progress_update: Dict[str, Tuple[datetime, float]] = {}
        self.node_timeout_seconds: int = 300  # 5 minutes
        self.job_progress_timeout_seconds: int = 1800  # 30 minutes
        self.job_timeout_factors: Dict[str, float] = {}  # job_id -> timeout factor
        self.custom_detectors: List[Tuple[Callable, Dict[str, Any]]] = []
    
    def register_heartbeat(self, node_id: str) -> None:
        """
        Register a heartbeat from a node.
        
        Args:
            node_id: ID of the node
        """
        self.heartbeat_timestamps[node_id] = datetime.now()
        
        # Check if there's an active node timeout failure and resolve it
        for failure_id, failure in list(self.active_failures.items()):
            if (failure.node_id == node_id and 
                failure.failure_type == FailureType.NODE_TIMEOUT and
                not failure.resolved):
                failure.resolve("Node heartbeat received")
                del self.active_failures[failure_id]
    
    def update_job_progress(self, job_id: str, progress: float) -> None:
        """
        Update the progress of a job.
        
        Args:
            job_id: ID of the job
            progress: Current progress (0.0 to 100.0)
        """
        self.last_progress_update[job_id] = (datetime.now(), progress)
        
        # Check if there's an active job timeout failure and resolve it
        for failure_id, failure in list(self.active_failures.items()):
            if (failure.job_id == job_id and 
                failure.failure_type == FailureType.JOB_TIMEOUT and
                not failure.resolved):
                failure.resolve("Job progress updated")
                del self.active_failures[failure_id]
    
    def set_job_timeout_factor(self, job_id: str, factor: float) -> None:
        """
        Set a custom timeout factor for a job.
        
        Args:
            job_id: ID of the job
            factor: Timeout factor (1.0 = normal timeout)
        """
        self.job_timeout_factors[job_id] = max(0.1, factor)
    
    def register_custom_detector(
        self, 
        detector_func: Callable[[List[BaseJob], List[BaseNode]], Optional[FailureEvent]],
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Register a custom failure detector function.
        
        Args:
            detector_func: Function that takes a list of jobs and nodes, and returns a failure event if detected
            config: Optional configuration for the detector
        """
        self.custom_detectors.append((detector_func, config or {}))
    
    def detect_failures(
        self,
        jobs: List[BaseJob],
        nodes: List[BaseNode],
    ) -> List[FailureEvent]:
        """
        Detect failures in jobs and nodes.
        
        Args:
            jobs: List of jobs to check
            nodes: List of nodes to check
            
        Returns:
            List of detected failure events
        """
        detected_failures: List[FailureEvent] = []
        
        # Check for node failures
        detected_failures.extend(self._detect_node_failures(nodes))
        
        # Check for job failures
        detected_failures.extend(self._detect_job_failures(jobs))
        
        # Run custom detectors
        for detector_func, config in self.custom_detectors:
            try:
                failure = detector_func(jobs, nodes)
                if failure:
                    detected_failures.append(failure)
                    self.active_failures[failure.id] = failure
                    self.failure_history.append(failure)
            except Exception as e:
                logger.error(f"Error in custom failure detector: {e}")
        
        return detected_failures
    
    def get_active_failures(
        self,
        node_id: Optional[str] = None,
        job_id: Optional[str] = None,
        failure_type: Optional[FailureType] = None,
        level: Optional[FailureLevel] = None,
    ) -> List[FailureEvent]:
        """
        Get active (unresolved) failures matching the filters.
        
        Args:
            node_id: Optional filter by node ID
            job_id: Optional filter by job ID
            failure_type: Optional filter by failure type
            level: Optional filter by failure level
            
        Returns:
            List of matching active failure events
        """
        filtered_failures = []
        
        for failure in self.active_failures.values():
            # Apply filters
            if node_id is not None and failure.node_id != node_id:
                continue
                
            if job_id is not None and failure.job_id != job_id:
                continue
                
            if failure_type is not None and failure.failure_type != failure_type:
                continue
                
            if level is not None and failure.level != level:
                continue
                
            filtered_failures.append(failure)
        
        return filtered_failures
    
    def get_failure_history(
        self,
        node_id: Optional[str] = None,
        job_id: Optional[str] = None,
        failure_type: Optional[FailureType] = None,
        level: Optional[FailureLevel] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        include_resolved: bool = True,
    ) -> List[FailureEvent]:
        """
        Get failure history matching the filters.
        
        Args:
            node_id: Optional filter by node ID
            job_id: Optional filter by job ID
            failure_type: Optional filter by failure type
            level: Optional filter by failure level
            start_time: Optional filter by start time
            end_time: Optional filter by end time
            include_resolved: Whether to include resolved failures
            
        Returns:
            List of matching failure events
        """
        filtered_failures = []
        
        for failure in self.failure_history:
            # Filter by resolution status
            if not include_resolved and failure.resolved:
                continue
                
            # Apply other filters
            if node_id is not None and failure.node_id != node_id:
                continue
                
            if job_id is not None and failure.job_id != job_id:
                continue
                
            if failure_type is not None and failure.failure_type != failure_type:
                continue
                
            if level is not None and failure.level != level:
                continue
                
            if start_time is not None and failure.timestamp < start_time:
                continue
                
            if end_time is not None and failure.timestamp > end_time:
                continue
                
            filtered_failures.append(failure)
        
        return filtered_failures
    
    def resolve_failure(
        self,
        failure_id: str,
        resolution_description: str = "Manually resolved",
    ) -> Result[bool]:
        """
        Resolve a failure.
        
        Args:
            failure_id: ID of the failure to resolve
            resolution_description: Description of how the failure was resolved
            
        Returns:
            Result with success status or error
        """
        # Check active failures
        if failure_id in self.active_failures:
            failure = self.active_failures[failure_id]
            failure.resolve(resolution_description)
            del self.active_failures[failure_id]
            return Result.ok(True)
        
        # Check historical failures
        for failure in self.failure_history:
            if failure.id == failure_id and not failure.resolved:
                failure.resolve(resolution_description)
                return Result.ok(True)
        
        return Result.err(f"Failure {failure_id} not found or already resolved")
    
    def _detect_node_failures(self, nodes: List[BaseNode]) -> List[FailureEvent]:
        """
        Detect failures in nodes.
        
        Args:
            nodes: List of nodes to check
            
        Returns:
            List of detected failure events
        """
        detected_failures = []
        now = datetime.now()
        
        # Create set of active node IDs
        active_node_ids = {node.id for node in nodes}
        
        # Check for offline nodes
        for node in nodes:
            if node.status == NodeStatus.OFFLINE:
                # Check if this is a new failure
                failure_key = f"node_offline_{node.id}"
                if failure_key not in self.active_failures:
                    # Create a new failure event
                    from uuid import uuid4
                    failure_id = f"failure_{uuid4().hex[:8]}"
                    failure = FailureEvent(
                        failure_id=failure_id,
                        failure_type=FailureType.NODE_OFFLINE,
                        level=FailureLevel.ERROR,
                        node_id=node.id,
                        description=f"Node {node.id} is offline",
                        details={"node_name": node.name},
                    )
                    
                    detected_failures.append(failure)
                    self.active_failures[failure_key] = failure
                    self.failure_history.append(failure)
            elif node.status in [NodeStatus.ERROR, NodeStatus.MAINTENANCE]:
                # Check if this is a new failure
                failure_key = f"node_error_{node.id}"
                if failure_key not in self.active_failures:
                    # Create a new failure event
                    from uuid import uuid4
                    failure_id = f"failure_{uuid4().hex[:8]}"
                    failure = FailureEvent(
                        failure_id=failure_id,
                        failure_type=FailureType.SYSTEM_FAILURE,
                        level=FailureLevel.WARNING,
                        node_id=node.id,
                        description=f"Node {node.id} is in {node.status.value} state",
                        details={
                            "node_name": node.name,
                            "status": node.status.value,
                            "error": node.last_error if hasattr(node, "last_error") else None,
                        },
                    )
                    
                    detected_failures.append(failure)
                    self.active_failures[failure_key] = failure
                    self.failure_history.append(failure)
            elif node.status == NodeStatus.ONLINE:
                # Resolve any existing offline/error failures
                for key in [f"node_offline_{node.id}", f"node_error_{node.id}"]:
                    if key in self.active_failures:
                        self.active_failures[key].resolve(f"Node {node.id} is now online")
                        del self.active_failures[key]
        
        # Check for node timeouts (missing heartbeats)
        for node_id, last_heartbeat in list(self.heartbeat_timestamps.items()):
            # Skip if node isn't in the current list (may have been removed)
            if node_id not in active_node_ids:
                continue
                
            timeout_duration = timedelta(seconds=self.node_timeout_seconds)
            if now - last_heartbeat > timeout_duration:
                # Check if this is a new failure
                failure_key = f"node_timeout_{node_id}"
                if failure_key not in self.active_failures:
                    # Create a new failure event
                    from uuid import uuid4
                    failure_id = f"failure_{uuid4().hex[:8]}"
                    failure = FailureEvent(
                        failure_id=failure_id,
                        failure_type=FailureType.NODE_TIMEOUT,
                        level=FailureLevel.WARNING,
                        node_id=node_id,
                        description=f"Node {node_id} has not sent a heartbeat for {timeout_duration.total_seconds()} seconds",
                        details={
                            "last_heartbeat_time": last_heartbeat.isoformat(),
                            "timeout_seconds": self.node_timeout_seconds,
                        },
                    )
                    
                    detected_failures.append(failure)
                    self.active_failures[failure_key] = failure
                    self.failure_history.append(failure)
        
        return detected_failures
    
    def _detect_job_failures(self, jobs: List[BaseJob]) -> List[FailureEvent]:
        """
        Detect failures in jobs.
        
        Args:
            jobs: List of jobs to check
            
        Returns:
            List of detected failure events
        """
        detected_failures = []
        now = datetime.now()
        
        # Check for failed jobs
        for job in jobs:
            if job.status == JobStatus.FAILED:
                # Check if this is a new failure
                failure_key = f"job_error_{job.id}"
                if failure_key not in self.active_failures:
                    # Create a new failure event
                    from uuid import uuid4
                    failure_id = f"failure_{uuid4().hex[:8]}"
                    
                    # Extract error message if available
                    error_message = "Unknown error"
                    if hasattr(job, "error_message") and job.error_message:
                        error_message = job.error_message
                    elif hasattr(job, "last_error") and job.last_error:
                        error_message = job.last_error
                    
                    failure = FailureEvent(
                        failure_id=failure_id,
                        failure_type=FailureType.JOB_ERROR,
                        level=FailureLevel.ERROR,
                        job_id=job.id,
                        description=f"Job {job.id} has failed: {error_message}",
                        details={
                            "job_name": job.name,
                            "error_count": getattr(job, "error_count", 1),
                            "assigned_node_id": job.assigned_node_id,
                        },
                    )
                    
                    detected_failures.append(failure)
                    self.active_failures[failure_key] = failure
                    self.failure_history.append(failure)
            
            # Check for jobs that missed deadlines
            if hasattr(job, "deadline") and job.deadline:
                if now > job.deadline and job.status not in [JobStatus.COMPLETED, JobStatus.CANCELLED]:
                    # Check if this is a new failure
                    failure_key = f"job_deadline_{job.id}"
                    if failure_key not in self.active_failures:
                        # Create a new failure event
                        from uuid import uuid4
                        failure_id = f"failure_{uuid4().hex[:8]}"
                        
                        failure = FailureEvent(
                            failure_id=failure_id,
                            failure_type=FailureType.JOB_TIMEOUT,
                            level=FailureLevel.WARNING,
                            job_id=job.id,
                            description=f"Job {job.id} has missed its deadline",
                            details={
                                "job_name": job.name,
                                "deadline": job.deadline.isoformat(),
                                "current_time": now.isoformat(),
                                "status": job.status.value,
                                "progress": job.progress,
                            },
                        )
                        
                        detected_failures.append(failure)
                        self.active_failures[failure_key] = failure
                        self.failure_history.append(failure)
            
            # Check for jobs that have stopped making progress
            if job.status == JobStatus.RUNNING and job.id in self.last_progress_update:
                last_update_time, last_progress = self.last_progress_update[job.id]
                
                # Get timeout duration, adjusted by job-specific factor
                timeout_seconds = self.job_progress_timeout_seconds
                if job.id in self.job_timeout_factors:
                    timeout_seconds *= self.job_timeout_factors[job.id]
                
                timeout_duration = timedelta(seconds=timeout_seconds)
                
                if now - last_update_time > timeout_duration and job.progress == last_progress:
                    # Check if this is a new failure
                    failure_key = f"job_timeout_{job.id}"
                    if failure_key not in self.active_failures:
                        # Create a new failure event
                        from uuid import uuid4
                        failure_id = f"failure_{uuid4().hex[:8]}"
                        
                        failure = FailureEvent(
                            failure_id=failure_id,
                            failure_type=FailureType.JOB_TIMEOUT,
                            level=FailureLevel.WARNING,
                            job_id=job.id,
                            description=f"Job {job.id} has not made progress for {timeout_duration.total_seconds()} seconds",
                            details={
                                "job_name": job.name,
                                "last_update_time": last_update_time.isoformat(),
                                "last_progress": last_progress,
                                "current_progress": job.progress,
                                "timeout_seconds": timeout_seconds,
                            },
                        )
                        
                        detected_failures.append(failure)
                        self.active_failures[failure_key] = failure
                        self.failure_history.append(failure)
        
        return detected_failures