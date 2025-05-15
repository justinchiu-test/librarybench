"""
Common exceptions for the unified concurrent task scheduler.

This module defines custom exceptions that are shared between
the render farm manager and scientific computing implementations.
"""

class TaskSchedulerError(Exception):
    """Base class for all task scheduler exceptions."""
    pass


class ResourceError(TaskSchedulerError):
    """Base class for resource-related errors."""
    pass


class ResourceNotAvailableError(ResourceError):
    """Raised when a requested resource is not available."""
    pass


class ResourceExceededError(ResourceError):
    """Raised when resource usage exceeds allocation."""
    pass


class DependencyError(TaskSchedulerError):
    """Base class for dependency-related errors."""
    pass


class CyclicDependencyError(DependencyError):
    """Raised when a cyclic dependency is detected."""
    pass


class DependencyNotFoundError(DependencyError):
    """Raised when a dependency is not found."""
    pass


class SchedulingError(TaskSchedulerError):
    """Base class for scheduling-related errors."""
    pass


class DeadlineMissedError(SchedulingError):
    """Raised when a job's deadline cannot be met."""
    pass


class PreemptionNotAllowedError(SchedulingError):
    """Raised when trying to preempt a job that cannot be preempted."""
    pass


class CheckpointError(TaskSchedulerError):
    """Base class for checkpoint-related errors."""
    pass


class CheckpointCreationError(CheckpointError):
    """Raised when checkpoint creation fails."""
    pass


class CheckpointRestoreError(CheckpointError):
    """Raised when checkpoint restoration fails."""
    pass


class CheckpointNotFoundError(CheckpointError):
    """Raised when a checkpoint is not found."""
    pass


class ValidationError(TaskSchedulerError):
    """Raised when validation fails."""
    pass


class AuthorizationError(TaskSchedulerError):
    """Raised when an operation is not authorized."""
    pass


class ConfigurationError(TaskSchedulerError):
    """Raised when there is a configuration error."""
    pass


class TimeoutError(TaskSchedulerError):
    """Raised when an operation times out."""
    pass


class NodeError(TaskSchedulerError):
    """Base class for node-related errors."""
    pass


class NodeOfflineError(NodeError):
    """Raised when a node is offline."""
    pass


class NodeMaintenanceError(NodeError):
    """Raised when a node is in maintenance."""
    pass


class NodeCapacityError(NodeError):
    """Raised when a node does not have sufficient capacity."""
    pass