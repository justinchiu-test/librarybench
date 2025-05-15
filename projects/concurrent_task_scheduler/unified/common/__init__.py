"""
Common functionality for the unified concurrent task scheduler.

This package provides shared models, interfaces, and utilities that can be used
by both the render farm manager and scientific computing implementations.
"""

__version__ = "0.1.0"

from common.core import (
    # Models
    AuditLogEntry,
    BaseJob,
    BaseNode,
    Checkpoint,
    CheckpointStatus,
    CheckpointType,
    Dependency,
    DependencyState,
    DependencyType,
    JobStatus,
    LogLevel,
    NodeStatus,
    Priority,
    ResourceRequirement,
    ResourceType,
    Result,
    TimeRange,
    
    # Interfaces
    AuditLogInterface,
    CheckpointManagerInterface,
    DependencyTrackerInterface,
    ResourceForecastingInterface,
    ResourceManagerInterface,
    SchedulerInterface,
    
    # Utilities
    DateTimeEncoder,
    ExponentialBackoff,
    PerformanceTimer,
    calculate_hash,
    create_directory_if_not_exists,
    datetime_decoder,
    deserialize_model,
    generate_id,
    serialize_model,
    weighted_average,
    
    # Exceptions
    AuthorizationError,
    CheckpointCreationError,
    CheckpointError,
    CheckpointNotFoundError,
    CheckpointRestoreError,
    ConfigurationError,
    CyclicDependencyError,
    DeadlineMissedError,
    DependencyError,
    DependencyNotFoundError,
    NodeCapacityError,
    NodeError,
    NodeMaintenanceError,
    NodeOfflineError,
    PreemptionNotAllowedError,
    ResourceError,
    ResourceExceededError,
    ResourceNotAvailableError,
    SchedulingError,
    TaskSchedulerError,
    TimeoutError,
    ValidationError,
)

from common.dependency_tracking import (
    DependencyGraph,
    DependencyTracker,
    WorkflowManager,
)

from common.job_management import (
    # Queue management
    JobQueue,
    QueuePolicy,
    FairnessMetric,
    QueuedJob,
    QueueStats,
    PreemptionAction,
    PreemptionTrigger,
    PreemptionPolicy,
    
    # Job scheduling
    JobScheduler,
    
    # Priority management
    PriorityManager,
    PriorityPolicy,
    PriorityInheritanceMode,
)