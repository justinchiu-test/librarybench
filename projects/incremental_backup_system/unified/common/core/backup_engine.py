"""
Core backup engine for the unified incremental backup system.

This module provides the base backup engine implementation and interfaces.
"""

import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any

from common.core.models import BackupConfig, FileInfo, VersionInfo, VersionType
from common.core.storage import StorageManager, FileSystemStorageManager
from common.core.versioning import VersionTracker, FileSystemVersionTracker
from common.core.utils import (
    calculate_file_hash, detect_file_type, scan_directory,
    get_file_size, get_file_modification_time, is_binary_file,
    create_unique_id, generate_timestamp, save_json, load_json
)
from common.core.chunking import ChunkingStrategy, RollingHashChunker


class BaseBackupEngine(ABC):
    """Base interface for the backup engine."""
    
    @abstractmethod
    def initialize_repository(self, root_path: Path) -> bool:
        """Initialize a new backup repository at the specified path.
        
        Args:
            root_path: Path where the backup repository will be created
            
        Returns:
            bool: True if initialization was successful
        """
        pass
    
    @abstractmethod
    def create_snapshot(self, source_path: Path, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new snapshot of the source directory.
        
        Args:
            source_path: Path to the directory to backup
            metadata: Optional metadata to store with the snapshot
            
        Returns:
            str: Unique ID of the created snapshot
        """
        pass
    
    @abstractmethod
    def restore_snapshot(
        self, 
        snapshot_id: str, 
        target_path: Path,
        excluded_paths: Optional[List[str]] = None
    ) -> bool:
        """Restore a specific snapshot to the target path.
        
        Args:
            snapshot_id: ID of the snapshot to restore
            target_path: Path where the snapshot will be restored
            excluded_paths: Optional list of paths to exclude from restoration
            
        Returns:
            bool: True if restore was successful
        """
        pass
    
    @abstractmethod
    def get_snapshot_info(self, snapshot_id: str) -> Dict[str, Any]:
        """Get metadata about a specific snapshot.
        
        Args:
            snapshot_id: ID of the snapshot
            
        Returns:
            Dict containing snapshot metadata
        """
        pass
    
    @abstractmethod
    def list_snapshots(self, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List all snapshots matching the filter criteria.
        
        Args:
            filter_criteria: Optional criteria to filter snapshots
            
        Returns:
            List of dictionaries containing snapshot metadata
        """
        pass
    
    @abstractmethod
    def get_version_diff(self, version_id1: str, version_id2: str) -> Dict[str, str]:
        """Get differences between two versions.
        
        Args:
            version_id1: ID of the first version
            version_id2: ID of the second version
            
        Returns:
            Dict[str, str]: Dictionary of file paths to change types
                (added, modified, deleted, unchanged)
        """
        pass
    
    @abstractmethod
    def get_storage_stats(self) -> Dict[str, int]:
        """Get statistics about the backup storage.
        
        Returns:
            Dict containing storage statistics
        """
        pass


class IncrementalBackupEngine(BaseBackupEngine):
    """Default implementation of the incremental backup engine."""
    
    def __init__(
        self,
        project_name: str,
        config: Optional[BackupConfig] = None,
        storage_manager: Optional[StorageManager] = None,
        version_tracker: Optional[VersionTracker] = None,
        chunking_strategy: Optional[ChunkingStrategy] = None
    ):
        """Initialize the backup engine.
        
        Args:
            project_name: Name of the project
            config: Optional configuration for the backup engine
            storage_manager: Optional storage manager to use
            version_tracker: Optional version tracker to use
            chunking_strategy: Optional chunking strategy to use
        """
        self.project_name = project_name
        self.config = config or BackupConfig(repository_path=Path("backups"))
        self._repository_path = self.config.repository_path
        
        # Create repository directory structure
        self._repository_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.storage_manager = storage_manager or FileSystemStorageManager(
            self._repository_path, 
            chunking_strategy or RollingHashChunker(
                min_chunk_size=self.config.min_chunk_size,
                max_chunk_size=self.config.max_chunk_size
            )
        )
        
        self.version_tracker = version_tracker or FileSystemVersionTracker(
            project_name,
            self._repository_path
        )
        
        # Cache for file hashes to avoid recalculating
        self._hash_cache: Dict[Path, str] = {}
    
    def initialize_repository(self, root_path: Path) -> bool:
        """Initialize a new backup repository at the specified path.
        
        Args:
            root_path: Path where the backup repository will be created
            
        Returns:
            bool: True if initialization was successful
        """
        try:
            # Update repository path
            self._repository_path = root_path
            
            # Create directory structure
            os.makedirs(root_path / "versions", exist_ok=True)
            os.makedirs(root_path / "files", exist_ok=True)
            os.makedirs(root_path / "chunks", exist_ok=True)
            os.makedirs(root_path / "metadata", exist_ok=True)
            
            # Create repository metadata
            repo_metadata = {
                "version": "1.0.0",
                "created_at": generate_timestamp(),
                "project_name": self.project_name,
                "config": self.config.model_dump() if hasattr(self.config, "model_dump") else self.config.__dict__
            }
            
            save_json(repo_metadata, root_path / "repository.json")
            
            # Update config with new path
            self.config.repository_path = root_path
            
            # Reinitialize components with new path
            chunking_strategy = getattr(self.storage_manager, "chunking_strategy", None)
            self.storage_manager = FileSystemStorageManager(
                root_path, 
                chunking_strategy
            )
            
            self.version_tracker = FileSystemVersionTracker(
                self.project_name,
                root_path
            )
            
            return True
        except Exception as e:
            print(f"Failed to initialize repository: {e}")
            return False
    
    def _scan_project_files(self, source_path: Path) -> List[FileInfo]:
        """Scan a project directory for files.
        
        Args:
            source_path: Path to the project directory
            
        Returns:
            List of FileInfo objects
        """
        # Get all files in the source directory, excluding patterns from config
        file_paths = scan_directory(source_path, exclude_patterns=self.config.ignore_patterns)
        
        # Create FileInfo objects for each file
        file_infos = []
        for full_path in file_paths:
            rel_path = full_path.relative_to(source_path)
            size = get_file_size(full_path)
            modified_time = get_file_modification_time(full_path)
            is_binary = is_binary_file(full_path, self.config.binary_extensions)
            content_type = detect_file_type(full_path)
            
            file_infos.append(FileInfo(
                path=str(rel_path),
                size=size,
                hash="",  # Will be calculated later
                modified_time=modified_time,
                is_binary=is_binary,
                content_type=content_type
            ))
        
        return file_infos
    
    def _process_file(
        self, 
        file_path: Path, 
        source_path: Path,
        is_binary: bool
    ) -> FileInfo:
        """Process a file for backup.
        
        Args:
            file_path: Relative path to the file
            source_path: Path to the source directory
            is_binary: Whether the file is binary
            
        Returns:
            FileInfo: Information about the processed file
        """
        full_path = source_path / file_path
        size = get_file_size(full_path)
        modified_time = get_file_modification_time(full_path)
        
        if is_binary:
            # Binary files are chunked
            with open(full_path, "rb") as f:
                data = f.read()
            
            # Calculate file hash
            file_hash = calculate_file_hash(full_path)
            
            # Chunk the file
            chunks = self.storage_manager.chunking_strategy.chunk_data(
                data, 
                file_extension=full_path.suffix
            )
            
            # Store chunks
            chunk_ids = []
            for chunk in chunks:
                chunk_id = self.storage_manager.store_chunk(chunk)
                chunk_ids.append(chunk_id)
            
            return FileInfo(
                path=str(file_path),
                size=size,
                hash=file_hash,
                modified_time=modified_time,
                is_binary=True,
                content_type=detect_file_type(full_path),
                chunks=chunk_ids
            )
        else:
            # Text files are stored directly
            file_hash, storage_path = self.storage_manager.store_file(full_path)
            
            return FileInfo(
                path=str(file_path),
                size=size,
                hash=file_hash,
                modified_time=modified_time,
                is_binary=False,
                content_type=detect_file_type(full_path),
                storage_path=storage_path
            )
    
    def create_snapshot(self, source_path: Path, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new snapshot of the source directory.
        
        Args:
            source_path: Path to the directory to backup
            metadata: Optional metadata to store with the snapshot
            
        Returns:
            str: Unique ID of the created snapshot
        """
        source_path = Path(source_path)
        
        # Scan all files in the source directory
        current_files = self._scan_project_files(source_path)
        
        # Get the previous version if it exists
        prev_version = self.version_tracker.get_latest_version()
        
        # Create mappings for easier lookup
        current_files_dict = {file.path: file for file in current_files}
        
        # Detect changes and process files
        processed_files = {}
        
        if prev_version:
            # We have a previous version to compare against
            prev_files = prev_version.files
            
            # Check each current file
            for rel_path, file_info in current_files_dict.items():
                if rel_path in prev_files:
                    # File exists in previous version
                    prev_file = prev_files[rel_path]
                    
                    # Check if file has changed
                    if prev_file.modified_time != file_info.modified_time or prev_file.size != file_info.size:
                        # File has changed, process it
                        processed_file = self._process_file(
                            Path(rel_path), 
                            source_path,
                            file_info.is_binary
                        )
                        processed_files[rel_path] = processed_file
                    else:
                        # File hasn't changed, use info from previous version
                        processed_files[rel_path] = prev_file
                else:
                    # New file, process it
                    processed_file = self._process_file(
                        Path(rel_path), 
                        source_path,
                        file_info.is_binary
                    )
                    processed_files[rel_path] = processed_file
        else:
            # No previous version, process all files
            for rel_path, file_info in current_files_dict.items():
                processed_file = self._process_file(
                    Path(rel_path), 
                    source_path,
                    file_info.is_binary
                )
                processed_files[rel_path] = processed_file
        
        # Create a snapshot with the processed files
        version = self.version_tracker.create_version(
            name=f"Snapshot {generate_timestamp()}",
            files=processed_files,
            parent_id=prev_version.id if prev_version else None,
            description=metadata.get("description", "Automatic snapshot") if metadata else "Automatic snapshot",
            tags=metadata.get("tags", []) if metadata else [],
            is_milestone=metadata.get("is_milestone", False) if metadata else False
        )
        
        return version.id
    
    def restore_snapshot(
        self, 
        snapshot_id: str, 
        target_path: Path,
        excluded_paths: Optional[List[str]] = None
    ) -> bool:
        """Restore a specific snapshot to the target path.
        
        Args:
            snapshot_id: ID of the snapshot to restore
            target_path: Path where the snapshot will be restored
            excluded_paths: Optional list of paths to exclude from restoration
            
        Returns:
            bool: True if restore was successful
        """
        target_path = Path(target_path)
        
        try:
            # Get the version to restore
            version = self.version_tracker.get_version(snapshot_id)
            
            # Create the target directory if it doesn't exist
            os.makedirs(target_path, exist_ok=True)
            
            # Convert excluded paths to a set for faster lookup
            excluded = set(excluded_paths or [])
            
            # Restore each file
            for rel_path, file_info in version.files.items():
                if rel_path in excluded:
                    continue
                
                output_path = target_path / rel_path
                
                # Create parent directories if needed
                os.makedirs(output_path.parent, exist_ok=True)
                
                if file_info.is_binary and file_info.chunks:
                    # Restore binary file from chunks
                    with open(output_path, "wb") as f:
                        for chunk_id in file_info.chunks:
                            chunk_data = self.storage_manager.retrieve_chunk(chunk_id)
                            f.write(chunk_data)
                else:
                    # Restore text file
                    self.storage_manager.retrieve_file(file_info.hash, output_path)
            
            return True
        except Exception as e:
            print(f"Error restoring snapshot {snapshot_id}: {e}")
            return False
    
    def get_snapshot_info(self, snapshot_id: str) -> Dict[str, Any]:
        """Get metadata about a specific snapshot.
        
        Args:
            snapshot_id: ID of the snapshot
            
        Returns:
            Dict containing snapshot metadata
        """
        try:
            version = self.version_tracker.get_version(snapshot_id)
            return version.model_dump() if hasattr(version, "model_dump") else version.__dict__
        except Exception as e:
            raise ValueError(f"Error getting snapshot info: {e}")
    
    def list_snapshots(self, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List all snapshots matching the filter criteria.
        
        Args:
            filter_criteria: Optional criteria to filter snapshots
            
        Returns:
            List of dictionaries containing snapshot metadata
        """
        versions = self.version_tracker.list_versions(filter_criteria)
        return [
            v.model_dump() if hasattr(v, "model_dump") else v.__dict__
            for v in versions
        ]
    
    def get_version_diff(self, version_id1: str, version_id2: str) -> Dict[str, str]:
        """Get differences between two versions.
        
        Args:
            version_id1: ID of the first version
            version_id2: ID of the second version
            
        Returns:
            Dict[str, str]: Dictionary of file paths to change types
                (added, modified, deleted, unchanged)
        """
        # Get the versions
        version1 = self.version_tracker.get_version(version_id1)
        version2 = self.version_tracker.get_version(version_id2)
        
        diff = {}
        
        # Check for added, modified, or unchanged files
        for rel_path, file_info in version2.files.items():
            if rel_path not in version1.files:
                diff[rel_path] = "added"
            elif file_info.hash != version1.files[rel_path].hash:
                # Hash difference means content changed
                diff[rel_path] = "modified"
            elif file_info.size != version1.files[rel_path].size:
                # Size difference is another indicator of modification
                diff[rel_path] = "modified"
            elif file_info.modified_time != version1.files[rel_path].modified_time:
                # Modified time difference can indicate changes
                diff[rel_path] = "modified"
            else:
                diff[rel_path] = "unchanged"
        
        # Check for deleted files
        for rel_path in version1.files:
            if rel_path not in version2.files:
                diff[rel_path] = "deleted"
        
        return diff
    
    def get_storage_stats(self) -> Dict[str, int]:
        """Get statistics about the backup storage.
        
        Returns:
            Dict containing storage statistics
        """
        return self.storage_manager.get_storage_size()