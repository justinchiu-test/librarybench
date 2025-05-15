"""
Core components for the unified concurrent task scheduler.

This package contains the core models, interfaces, utilities, and exceptions
that are shared between the render farm manager and scientific computing implementations.
"""

from common.core.models import (
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
)

from common.core.interfaces import (
    AuditLogInterface,
    CheckpointManagerInterface,
    DependencyTrackerInterface,
    ResourceForecastingInterface,
    ResourceManagerInterface,
    SchedulerInterface,
)

from common.core.utils import (
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
)

from common.core.exceptions import (
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