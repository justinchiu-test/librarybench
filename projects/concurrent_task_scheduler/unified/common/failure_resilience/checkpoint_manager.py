"""
Checkpoint management for the unified concurrent task scheduler.

This module provides functionality for creating and restoring checkpoints that can be used
by both the render farm manager and scientific computing implementations.
"""

import json
import logging
import os
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union, BinaryIO

from common.core.exceptions import (
    CheckpointCreationError, 
    CheckpointNotFoundError,
    CheckpointRestoreError,
)
from common.core.interfaces import CheckpointManagerInterface
from common.core.models import (
    BaseJob,
    Checkpoint,
    CheckpointStatus,
    CheckpointType,
    JobStatus,
    Result,
)
from common.core.utils import (
    calculate_hash,
    create_directory_if_not_exists,
    generate_id,
    serialize_model,
    DateTimeEncoder,
)

logger = logging.getLogger(__name__)


class CheckpointManager(CheckpointManagerInterface):
    """
    Manager for creating and restoring checkpoints.
    
    This class is responsible for:
    1. Creating checkpoints for jobs/simulations
    2. Storing checkpoints in the file system
    3. Restoring jobs/simulations from checkpoints
    4. Managing checkpoint lifecycle
    """
    
    def __init__(
        self,
        base_directory: Optional[str] = None,
        retention_days: int = 7,
        max_checkpoints_per_job: int = 10,
    ):
        """
        Initialize the checkpoint manager.
        
        Args:
            base_directory: Root directory for storing checkpoints
            retention_days: Number of days to retain checkpoints
            max_checkpoints_per_job: Maximum number of checkpoints to keep per job
        """
        self.base_directory = base_directory or os.path.join(tempfile.gettempdir(), "checkpoints")
        self.retention_days = retention_days
        self.max_checkpoints_per_job = max_checkpoints_per_job
        self.checkpoints: Dict[str, Dict[str, Checkpoint]] = {}  # job_id -> checkpoint_id -> checkpoint
        
        # Create base directory if it doesn't exist
        create_directory_if_not_exists(self.base_directory)
    
    def create_checkpoint(
        self, 
        job: BaseJob,
        checkpoint_type: CheckpointType = CheckpointType.FULL,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Result[Checkpoint]:
        """
        Create a checkpoint for a job.
        
        Args:
            job: The job to checkpoint
            checkpoint_type: Type of checkpoint to create
            metadata: Optional metadata for the checkpoint
            
        Returns:
            Result with the created checkpoint or error
        """
        try:
            # Generate checkpoint ID and path
            checkpoint_id = generate_id(f"cp_{job.id}")
            job_directory = os.path.join(self.base_directory, job.id)
            create_directory_if_not_exists(job_directory)
            
            checkpoint_path = os.path.join(job_directory, f"{checkpoint_id}.json")
            
            # Create checkpoint object
            checkpoint = Checkpoint(
                id=checkpoint_id,
                job_id=job.id,
                checkpoint_type=checkpoint_type,
                status=CheckpointStatus.CREATED,
                path=checkpoint_path,
                metadata=metadata or {},
                creation_time=datetime.now(),
            )
            
            # Serialize job state
            job_state = serialize_model(job)
            
            # Add progress and status
            checkpoint.metadata["progress"] = job.progress
            checkpoint.metadata["status"] = job.status.value if isinstance(job.status, JobStatus) else job.status
            
            # Write checkpoint to file
            with open(checkpoint_path, 'w') as f:
                json.dump({
                    "checkpoint": serialize_model(checkpoint),
                    "job_state": job_state,
                }, f, cls=DateTimeEncoder, indent=2)
            
            # Update file size
            try:
                checkpoint.size_bytes = os.path.getsize(checkpoint_path)
            except OSError:
                checkpoint.size_bytes = 0
            
            # Calculate validation hash
            try:
                with open(checkpoint_path, 'rb') as f:
                    checkpoint.validation_hash = calculate_hash(f.read())
            except OSError:
                checkpoint.validation_hash = None
            
            # Update checkpoint status
            checkpoint.status = CheckpointStatus.COMPLETE
            
            # Update in-memory storage
            if job.id not in self.checkpoints:
                self.checkpoints[job.id] = {}
            
            self.checkpoints[job.id][checkpoint_id] = checkpoint
            
            # Enforce checkpoint limits
            self._enforce_retention_policies(job.id)
            
            # Update job with last_checkpoint_time
            if hasattr(job, 'last_checkpoint_time'):
                job.last_checkpoint_time = datetime.now()
                
            return Result.ok(checkpoint)
        
        except Exception as e:
            logger.error(f"Failed to create checkpoint for job {job.id}: {e}")
            return Result.err(f"Checkpoint creation failed: {str(e)}")
    
    def restore_checkpoint(
        self, 
        checkpoint_id: str,
        job_factory=None,  # Function to create a new job instance
    ) -> Result[BaseJob]:
        """
        Restore a job from a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint
            job_factory: Optional function to create a new job instance
            
        Returns:
            Result with the restored job or error
        """
        try:
            # Find checkpoint
            checkpoint = self._find_checkpoint(checkpoint_id)
            if not checkpoint:
                return Result.err(f"Checkpoint {checkpoint_id} not found")
            
            # Read checkpoint file
            try:
                with open(checkpoint.path, 'r') as f:
                    data = json.load(f)
            except (OSError, json.JSONDecodeError) as e:
                checkpoint.status = CheckpointStatus.FAILED
                return Result.err(f"Failed to read checkpoint file: {str(e)}")
            
            # Validate hash if available
            if checkpoint.validation_hash:
                with open(checkpoint.path, 'rb') as f:
                    current_hash = calculate_hash(f.read())
                
                if current_hash != checkpoint.validation_hash:
                    checkpoint.status = CheckpointStatus.FAILED
                    return Result.err("Checkpoint validation failed: hash mismatch")
            
            # Extract job state
            job_state = data.get("job_state")
            if not job_state:
                return Result.err("Invalid checkpoint: no job state found")
            
            # Use job factory if provided, otherwise use direct reconstruction
            restored_job = None
            if job_factory:
                # Call factory function with job state
                restored_job = job_factory(job_state)
            else:
                # Direct construction from state
                from pydantic import create_model_from_dict
                try:
                    # Try to recreate job using pydantic if possible
                    BaseJobModel = type(BaseJob)
                    if isinstance(BaseJobModel, type):
                        restored_job = BaseJobModel.parse_obj(job_state)
                except Exception:
                    # Fallback to simple dict
                    restored_job = job_state
            
            # Update checkpoint
            checkpoint.status = CheckpointStatus.RESTORED
            checkpoint.restore_count += 1
            checkpoint.last_restore_time = datetime.now()
            
            return Result.ok(restored_job)
        
        except Exception as e:
            logger.error(f"Failed to restore checkpoint {checkpoint_id}: {e}")
            return Result.err(f"Checkpoint restoration failed: {str(e)}")
    
    def get_latest_checkpoint(self, job_id: str) -> Optional[Checkpoint]:
        """
        Get the latest checkpoint for a job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            The latest checkpoint, or None if no checkpoints exist
        """
        if job_id not in self.checkpoints:
            return self._load_checkpoints_for_job(job_id)
        
        checkpoints = self.checkpoints[job_id]
        if not checkpoints:
            return None
        
        # Find the latest checkpoint by creation time
        return max(
            checkpoints.values(),
            key=lambda cp: cp.creation_time, 
            default=None
        )
    
    def list_checkpoints(self, job_id: str) -> List[Checkpoint]:
        """
        List all checkpoints for a job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            List of checkpoints
        """
        if job_id not in self.checkpoints:
            self._load_checkpoints_for_job(job_id)
        
        return list(self.checkpoints.get(job_id, {}).values())
    
    def delete_checkpoint(self, checkpoint_id: str) -> Result[bool]:
        """
        Delete a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint
            
        Returns:
            Result with success status or error
        """
        checkpoint = self._find_checkpoint(checkpoint_id)
        if not checkpoint:
            return Result.err(f"Checkpoint {checkpoint_id} not found")
        
        # Delete file
        try:
            os.remove(checkpoint.path)
        except OSError as e:
            logger.warning(f"Failed to delete checkpoint file {checkpoint.path}: {e}")
        
        # Remove from in-memory storage
        if checkpoint.job_id in self.checkpoints:
            self.checkpoints[checkpoint.job_id].pop(checkpoint_id, None)
        
        return Result.ok(True)
    
    def clean_expired_checkpoints(self) -> int:
        """
        Clean up expired checkpoints based on retention policy.
        
        Returns:
            Number of deleted checkpoints
        """
        deleted_count = 0
        
        # Get all job IDs
        job_ids = list(self.checkpoints.keys())
        
        # Load checkpoints from disk for jobs not yet in memory
        job_directories = [d for d in os.listdir(self.base_directory) 
                          if os.path.isdir(os.path.join(self.base_directory, d))]
        
        for job_id in job_directories:
            if job_id not in job_ids:
                self._load_checkpoints_for_job(job_id)
                job_ids.append(job_id)
        
        # Check each job's checkpoints
        for job_id in job_ids:
            deleted = self._enforce_retention_policies(job_id)
            deleted_count += deleted
        
        return deleted_count
    
    def validate_checkpoint(self, checkpoint_id: str) -> Result[bool]:
        """
        Validate a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint
            
        Returns:
            Result with validation status or error
        """
        checkpoint = self._find_checkpoint(checkpoint_id)
        if not checkpoint:
            return Result.err(f"Checkpoint {checkpoint_id} not found")
        
        # Check if file exists
        if not os.path.exists(checkpoint.path):
            checkpoint.status = CheckpointStatus.FAILED
            return Result.err(f"Checkpoint file not found: {checkpoint.path}")
        
        # Validate hash if available
        if checkpoint.validation_hash:
            try:
                with open(checkpoint.path, 'rb') as f:
                    current_hash = calculate_hash(f.read())
                
                if current_hash != checkpoint.validation_hash:
                    checkpoint.status = CheckpointStatus.FAILED
                    return Result.err("Checkpoint validation failed: hash mismatch")
            except OSError as e:
                return Result.err(f"Failed to read checkpoint file: {str(e)}")
        
        # Try to load the checkpoint
        try:
            with open(checkpoint.path, 'r') as f:
                data = json.load(f)
                
            if "checkpoint" not in data or "job_state" not in data:
                return Result.err("Invalid checkpoint format")
        except (OSError, json.JSONDecodeError) as e:
            return Result.err(f"Failed to parse checkpoint file: {str(e)}")
        
        # Update status
        checkpoint.status = CheckpointStatus.VERIFIED
        
        return Result.ok(True)
    
    def _find_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Find a checkpoint by ID across all jobs."""
        for job_checkpoints in self.checkpoints.values():
            if checkpoint_id in job_checkpoints:
                return job_checkpoints[checkpoint_id]
        
        # Try to load from disk
        base_path = Path(self.base_directory)
        for job_dir in base_path.iterdir():
            if not job_dir.is_dir():
                continue
                
            checkpoint_path = job_dir / f"{checkpoint_id}.json"
            if checkpoint_path.exists():
                with open(checkpoint_path, 'r') as f:
                    try:
                        data = json.load(f)
                        checkpoint_data = data.get("checkpoint", {})
                        
                        # Create checkpoint object
                        from common.core.utils import deserialize_model
                        checkpoint = deserialize_model(checkpoint_data, Checkpoint)
                        
                        # Add to in-memory storage
                        job_id = job_dir.name
                        if job_id not in self.checkpoints:
                            self.checkpoints[job_id] = {}
                        
                        self.checkpoints[job_id][checkpoint_id] = checkpoint
                        return checkpoint
                    except (json.JSONDecodeError, KeyError):
                        continue
        
        return None
    
    def _load_checkpoints_for_job(self, job_id: str) -> Optional[Checkpoint]:
        """Load checkpoints from disk for a job."""
        job_dir = os.path.join(self.base_directory, job_id)
        if not os.path.isdir(job_dir):
            self.checkpoints[job_id] = {}
            return None
        
        # Initialize storage for this job
        self.checkpoints[job_id] = {}
        
        # Find all checkpoint files
        latest_checkpoint = None
        latest_time = datetime.min
        
        for filename in os.listdir(job_dir):
            if not filename.endswith('.json'):
                continue
                
            checkpoint_path = os.path.join(job_dir, filename)
            
            try:
                with open(checkpoint_path, 'r') as f:
                    data = json.load(f)
                    checkpoint_data = data.get("checkpoint", {})
                    
                    # Create checkpoint object
                    from common.core.utils import deserialize_model
                    checkpoint = deserialize_model(checkpoint_data, Checkpoint)
                    
                    # Add to in-memory storage
                    self.checkpoints[job_id][checkpoint.id] = checkpoint
                    
                    # Check if this is the latest checkpoint
                    if checkpoint.creation_time > latest_time:
                        latest_time = checkpoint.creation_time
                        latest_checkpoint = checkpoint
            except (json.JSONDecodeError, KeyError):
                continue
        
        return latest_checkpoint
    
    def _enforce_retention_policies(self, job_id: str) -> int:
        """
        Enforce retention policies for a job's checkpoints.
        
        Returns number of deleted checkpoints.
        """
        if job_id not in self.checkpoints:
            return 0
            
        checkpoints = self.checkpoints[job_id]
        if not checkpoints:
            return 0
            
        deleted_count = 0
        
        # Check for expired checkpoints
        now = datetime.now()
        retention_cutoff = now - timedelta(days=self.retention_days)
        
        expired_ids = [
            cp_id for cp_id, cp in checkpoints.items()
            if cp.creation_time < retention_cutoff
        ]
        
        # Delete expired checkpoints
        for checkpoint_id in expired_ids:
            checkpoint = checkpoints.get(checkpoint_id)
            if checkpoint:
                try:
                    os.remove(checkpoint.path)
                    checkpoints.pop(checkpoint_id)
                    deleted_count += 1
                except OSError:
                    pass
        
        # Enforce max checkpoints per job
        if len(checkpoints) > self.max_checkpoints_per_job:
            # Sort by creation time, oldest first
            sorted_checkpoints = sorted(
                checkpoints.items(),
                key=lambda x: x[1].creation_time
            )
            
            # Keep only the newest checkpoints
            to_delete = sorted_checkpoints[:-self.max_checkpoints_per_job]
            
            for checkpoint_id, checkpoint in to_delete:
                try:
                    os.remove(checkpoint.path)
                    checkpoints.pop(checkpoint_id)
                    deleted_count += 1
                except (OSError, KeyError):
                    pass
        
        return deleted_count