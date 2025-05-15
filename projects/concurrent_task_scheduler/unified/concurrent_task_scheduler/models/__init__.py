"""Models for the concurrent task scheduler."""

# Re-export common models from the unified library
from common.core.models import (
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
    Priority as SimulationPriority,
    ResourceRequirement,
    ResourceType,
    Result,
    TimeRange,
)

from common.core.utils import (
    DateTimeEncoder,
    generate_id,
    datetime_decoder as datetime_parser,
)

# Legacy imports to maintain compatibility with tests
from concurrent_task_scheduler.models.checkpoint import (
    CheckpointCompression,
    CheckpointManager,
    CheckpointMetadata,
    CheckpointPolicy,
    CheckpointStorageType,
)
from concurrent_task_scheduler.models.resource_forecast import (
    ForecastAccuracy,
    ForecastPeriod,
    ResourceForecast,
    ResourceProjection,
    ResourceUsagePattern,
    ResourceUtilizationHistory,
    UtilizationDataPoint,
)
from concurrent_task_scheduler.models.scenario import (
    ComparisonResult,
    ResourceAllocation,
    ResearchObjective,
    Scenario,
    ScenarioEvaluationResult,
    ScenarioStatus,
    ScientificMetric,
)
from concurrent_task_scheduler.models.simulation import (
    ClusterStatus,
    ComputeNode,
    NodeType,
    Simulation,
    SimulationStage,
    SimulationStageStatus,
    SimulationStatus,
)
from concurrent_task_scheduler.models.utils import (
    PerformanceMetric,
    SystemEvent,
)

__all__ = [
    # Common models from unified library
    "BaseJob",
    "BaseNode",
    "Checkpoint",
    "CheckpointStatus",
    "CheckpointType",
    "Dependency",
    "DependencyState",
    "DependencyType",
    "JobStatus",
    "LogLevel",
    "NodeStatus",
    "SimulationPriority",
    "ResourceRequirement",
    "ResourceType", 
    "Result",
    "TimeRange",
    
    # Checkpoint models
    "CheckpointCompression",
    "CheckpointManager",
    "CheckpointMetadata",
    "CheckpointPolicy",
    "CheckpointStorageType",
    
    # Resource forecast models
    "ForecastAccuracy",
    "ForecastPeriod",
    "ResourceForecast",
    "ResourceProjection",
    "ResourceUsagePattern",
    "ResourceUtilizationHistory",
    "UtilizationDataPoint",
    
    # Scenario models
    "ComparisonResult",
    "ResourceAllocation",
    "ResearchObjective",
    "Scenario",
    "ScenarioEvaluationResult",
    "ScenarioStatus",
    "ScientificMetric",
    
    # Simulation models
    "ClusterStatus",
    "ComputeNode",
    "NodeType",
    "Simulation",
    "SimulationStage",
    "SimulationStageStatus",
    "SimulationStatus",
    
    # Utility models
    "DateTimeEncoder",
    "PerformanceMetric",
    "SystemEvent",
    "datetime_parser",
    "generate_id",
]