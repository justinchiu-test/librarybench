"""Checkpoint management for simulation state preservation. Import wrapper for refactored version."""

# Import from refactored version - redirects all imports to the new implementation
from concurrent_task_scheduler.failure_resilience.checkpoint_manager_refactored import (
    CheckpointManager,
    CheckpointCoordinator,
    ValidationResult,
    CheckpointCreationStrategy,
    map_checkpoint_type_to_common,
    map_checkpoint_status_to_common,
    map_common_checkpoint_to_domain,
    simulation_to_job,
)

# Import required models from original location for test compatibility
from concurrent_task_scheduler.models.checkpoint import (
    Checkpoint,
    CheckpointCompression,
    CheckpointManager as CheckpointManagerModel,
    CheckpointMetadata,
    CheckpointPolicy,
    CheckpointStatus,
    CheckpointStorageType, 
    CheckpointType,
)

# Define mapping functions for backward compatibility
def map_common_checkpoint_type_to_domain(common_type):
    """Map common checkpoint type to domain-specific checkpoint type."""
    mapping = {
        "full": CheckpointType.FULL,
        "incremental": CheckpointType.INCREMENTAL,
        "metadata": CheckpointType.METADATA_ONLY,
        "delta": CheckpointType.INCREMENTAL,
    }
    return mapping.get(common_type, CheckpointType.FULL)

def map_common_checkpoint_status_to_domain(common_status):
    """Map common checkpoint status to domain-specific checkpoint status."""
    mapping = {
        "pending": CheckpointStatus.CREATING,
        "creating": CheckpointStatus.CREATING,
        "complete": CheckpointStatus.COMPLETE,
        "failed": CheckpointStatus.FAILED,
        "restoring": CheckpointStatus.CREATING,
        "restored": CheckpointStatus.COMPLETE,
        "deleted": CheckpointStatus.ARCHIVED,
    }
    return mapping.get(common_status, CheckpointStatus.CREATING)