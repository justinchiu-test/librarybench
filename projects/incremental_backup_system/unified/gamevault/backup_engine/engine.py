"""
Core backup engine for GameVault.

This module provides the main backup engine functionality.
"""

from pathlib import Path
from typing import Dict, List, Optional, Union

from common.core.backup_engine import IncrementalBackupEngine
from common.core.chunking import ChunkingStrategy, RollingHashChunker
from common.core.storage import StorageManager, FileSystemStorageManager
from common.core.versioning import VersionTracker, FileSystemVersionTracker
from common.core.models import VersionInfo

from gamevault.config import get_config
from gamevault.models import FileInfo, GameVersionType, ProjectVersion


class BackupEngine:
    """
    Core backup engine for GameVault.
    
    This class orchestrates the backup process, managing file scanning,
    change detection, storage, and version tracking.
    """
    
    def __init__(
        self,
        project_name: str,
        project_path: Union[str, Path],
        storage_dir: Optional[Union[str, Path]] = None,
        chunking_strategy: Optional[ChunkingStrategy] = None
    ):
        """
        Initialize the backup engine.
        
        Args:
            project_name: Name of the project
            project_path: Path to the project directory
            storage_dir: Directory where backups will be stored. If None, uses the default from config.
            chunking_strategy: Strategy for chunking binary files. If None, uses RollingHashChunker.
        """
        config = get_config()
        self.config = config
        self.project_name = project_name
        self.project_path = Path(project_path)
        
        # Directory for storing backups
        self.storage_dir = Path(storage_dir) if storage_dir else config.backup_dir
        
        # Set chunking strategy
        self.chunking_strategy = chunking_strategy or RollingHashChunker(
            min_chunk_size=config.min_chunk_size,
            max_chunk_size=config.max_chunk_size
        )
        
        # Initialize common components using the unified library
        # Create a custom storage manager
        self.storage_manager = FileSystemStorageManager(
            self.storage_dir,
            self.chunking_strategy
        )
        
        # Create a custom version tracker
        self.version_tracker = FileSystemVersionTracker(
            project_name,
            self.storage_dir
        )
        
        # Create the core backup engine
        self._engine = IncrementalBackupEngine(
            project_name=project_name,
            config=None,  # Use default config from the engine
            storage_manager=self.storage_manager,
            version_tracker=self.version_tracker,
            chunking_strategy=self.chunking_strategy
        )
        
        # Set the project path for the engine
        self._engine.project_path = self.project_path
    
    def create_backup(
        self,
        name: str,
        version_type: GameVersionType = GameVersionType.DEVELOPMENT,
        description: Optional[str] = None,
        is_milestone: bool = False,
        tags: Optional[List[str]] = None
    ) -> ProjectVersion:
        """
        Create a backup of the project.
        
        Args:
            name: Name of the backup version
            version_type: Type of the version
            description: Description of the version
            is_milestone: Whether this version is a milestone
            tags: List of tags for this version
            
        Returns:
            ProjectVersion: The created version
        """
        # Use the common engine to create the snapshot
        metadata = {
            "description": description,
            "tags": tags or [],
            "is_milestone": is_milestone,
            "version_type": version_type
        }
        
        # Create the snapshot
        snapshot_id = self._engine.create_snapshot(self.project_path, metadata)
        
        # Get the version information
        version_info = self._engine.version_tracker.get_version(snapshot_id)
        
        # Convert to ProjectVersion for API compatibility
        # Convert files from common.core.models.FileInfo to gamevault.models.FileInfo
        converted_files = {}
        for path, file_info in version_info.files.items():
            converted_files[path] = FileInfo(
                path=file_info.path,
                size=file_info.size,
                hash=file_info.hash,
                modified_time=file_info.modified_time,
                is_binary=file_info.is_binary,
                chunks=file_info.chunks,
                storage_path=file_info.storage_path,
                metadata=file_info.metadata or {}
            )
            
        return ProjectVersion(
            id=version_info.id,
            timestamp=version_info.timestamp,
            name=name,
            parent_id=version_info.parent_id,
            type=version_type,
            tags=tags or [],
            description=description,
            files=converted_files,
            is_milestone=is_milestone
        )
    
    def restore_version(
        self,
        version_id: str,
        output_path: Optional[Union[str, Path]] = None,
        excluded_paths: Optional[List[str]] = None
    ) -> Path:
        """
        Restore a version of the project.
        
        Args:
            version_id: ID of the version to restore
            output_path: Path where the version should be restored. If None, creates a new directory.
            excluded_paths: List of file paths to exclude from restoration
            
        Returns:
            Path: Path to the restored project
            
        Raises:
            FileNotFoundError: If the version doesn't exist
        """
        # Determine output path
        if output_path is None:
            from gamevault.utils import generate_timestamp
            timestamp = int(generate_timestamp())
            output_path = self.project_path.parent / f"{self.project_name}_restore_{timestamp}"
        
        output_path = Path(output_path)
        
        # Use the common engine to restore the snapshot
        self._engine.restore_snapshot(version_id, output_path, excluded_paths)
        
        return output_path
    
    def get_version_diff(
        self, 
        version_id1: str, 
        version_id2: str
    ) -> Dict[str, str]:
        """
        Get the differences between two versions.
        
        Args:
            version_id1: ID of the first version
            version_id2: ID of the second version
            
        Returns:
            Dict[str, str]: Dictionary of file paths to change types
                (added, modified, deleted, unchanged)
        """
        return self._engine.get_version_diff(version_id1, version_id2)
    
    def get_storage_stats(self) -> Dict[str, int]:
        """
        Get statistics about the backup storage.
        
        Returns:
            Dict[str, int]: Dictionary with storage statistics
        """
        return self._engine.get_storage_stats()