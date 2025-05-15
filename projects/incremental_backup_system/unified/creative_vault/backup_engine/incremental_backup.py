"""
Incremental Backup Engine for artistic content.

This module provides the core functionality for detecting changes, creating
deltas, and maintaining version history of creative files.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from common.core.backup_engine import IncrementalBackupEngine
from common.core.models import BackupConfig
from creative_vault.interfaces import BackupEngine


class DeltaBackupEngine(BackupEngine):
    """Implementation of the incremental backup engine using delta storage for creative content."""
    
    def __init__(self, config: Optional[BackupConfig] = None):
        """Initialize the backup engine.
        
        Args:
            config: Optional configuration for the backup engine
        """
        self.config = config or BackupConfig(repository_path=Path("backups"))
        
        # Create the common implementation
        self._engine = IncrementalBackupEngine(
            project_name="creative_vault",
            config=self.config
        )
        
        # For compatibility with old code
        self._repository_path = self.config.repository_path
        self._snapshots_path = self._repository_path / "versions"
        self._objects_path = self._repository_path / "files"
        self._metadata_path = self._repository_path / "metadata"
    
    def initialize_repository(self, root_path: Path) -> bool:
        """Initialize a new backup repository at the specified path.
        
        Args:
            root_path: Path where the backup repository will be created
            
        Returns:
            bool: True if initialization was successful
        """
        # Initialize the repository
        success = self._engine.initialize_repository(root_path)
        
        # Update local paths for compatibility with tests
        if success:
            self._repository_path = root_path
            self._snapshots_path = self._repository_path / "versions"
            self._objects_path = self._repository_path / "files"
            self._metadata_path = self._repository_path / "metadata"
        
        return success
    
    def create_snapshot(self, source_path: Path, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new snapshot of the source directory.
        
        Args:
            source_path: Path to the directory to backup
            metadata: Optional metadata to store with the snapshot
            
        Returns:
            str: Unique ID of the created snapshot
        """
        return self._engine.create_snapshot(source_path, metadata)
    
    def restore_snapshot(self, snapshot_id: str, target_path: Path) -> bool:
        """Restore a specific snapshot to the target path.
        
        Args:
            snapshot_id: ID of the snapshot to restore
            target_path: Path where the snapshot will be restored
            
        Returns:
            bool: True if restore was successful
        """
        return self._engine.restore_snapshot(snapshot_id, target_path)
    
    def get_snapshot_info(self, snapshot_id: str) -> Dict[str, Any]:
        """Get metadata about a specific snapshot.
        
        Args:
            snapshot_id: ID of the snapshot
            
        Returns:
            Dict containing snapshot metadata
        """
        return self._engine.get_snapshot_info(snapshot_id)
    
    def list_snapshots(self, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List all snapshots matching the filter criteria.
        
        Args:
            filter_criteria: Optional criteria to filter snapshots
            
        Returns:
            List of dictionaries containing snapshot metadata
        """
        return self._engine.list_snapshots(filter_criteria)
    
    def get_version_diff(self, version_id1: str, version_id2: str) -> Dict[str, str]:
        """Get differences between two versions.
        
        Args:
            version_id1: ID of the first version
            version_id2: ID of the second version
            
        Returns:
            Dict[str, str]: Dictionary of file paths to change types
        """
        # Add conversion from internal path objects to strings for compatibility
        diff_dict = self._engine.get_version_diff(version_id1, version_id2)
        
        # Convert keys to Path objects for compatibility with older tests
        result = {}
        for path_str, diff_type in diff_dict.items():
            result[Path(path_str)] = diff_type
            
        return result
    
    def get_storage_stats(self) -> Dict[str, int]:
        """Get statistics about the backup storage.
        
        Returns:
            Dict containing storage statistics
        """
        return self._engine.get_storage_stats()
    
    def _get_latest_snapshot(self) -> Optional[str]:
        """Get the ID of the most recent snapshot.
        
        Returns:
            str: The ID of the most recent snapshot, or None if no snapshots exist
        """
        version = self._engine.version_tracker.get_latest_version()
        return version.id if version else None