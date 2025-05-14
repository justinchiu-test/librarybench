"""
Incremental Backup Engine for artistic content.

This module provides the core functionality for detecting changes, creating
deltas, and maintaining version history of creative files.
"""

import json
import os
import shutil
import tempfile
import time
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import numpy as np
from pydantic import BaseModel, Field

from creative_vault.interfaces import BackupEngine
from creative_vault.utils import (BackupConfig, FileInfo, calculate_file_hash, 
                                create_timestamp, create_unique_id, detect_file_type,
                                load_json, save_json, scan_directory)


class SnapshotInfo(BaseModel):
    """Information about a backup snapshot."""
    
    id: str
    timestamp: datetime
    source_path: Path
    files_count: int
    total_size: int
    new_files: List[Path]
    modified_files: List[Path]
    deleted_files: List[Path]
    metadata: Dict[str, Any] = {}


class DeltaBackupEngine(BackupEngine):
    """Implementation of the incremental backup engine using delta storage."""
    
    def __init__(self, config: Optional[BackupConfig] = None):
        """Initialize the backup engine.
        
        Args:
            config: Optional configuration for the backup engine
        """
        self.config = config or BackupConfig(repository_path=Path("backups"))
        self._repository_path = self.config.repository_path
        self._snapshots_path = self._repository_path / "snapshots"
        self._objects_path = self._repository_path / "objects"
        self._metadata_path = self._repository_path / "metadata"
        
        # Cache of file hashes to avoid recalculating
        self._hash_cache: Dict[Path, str] = {}
        
        # Cache of file metadata
        self._file_metadata_cache: Dict[Path, Dict[str, Any]] = {}
    
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
            self._snapshots_path = self._repository_path / "snapshots"
            self._objects_path = self._repository_path / "objects"
            self._metadata_path = self._repository_path / "metadata"
            
            # Create directory structure
            self._snapshots_path.mkdir(parents=True, exist_ok=True)
            self._objects_path.mkdir(parents=True, exist_ok=True)
            self._metadata_path.mkdir(parents=True, exist_ok=True)
            
            # Create repository metadata
            repo_metadata = {
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
                "config": self.config.model_dump(),
            }
            save_json(repo_metadata, self._repository_path / "repository.json")
            
            return True
        except Exception as e:
            print(f"Failed to initialize repository: {e}")
            return False
    
    def create_snapshot(self, source_path: Path, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new snapshot of the source directory.
        
        Args:
            source_path: Path to the directory to backup
            metadata: Optional metadata to store with the snapshot
            
        Returns:
            str: Unique ID of the created snapshot
        """
        snapshot_id = create_unique_id("snapshot-")
        snapshot_path = self._snapshots_path / snapshot_id
        snapshot_path.mkdir(parents=True, exist_ok=True)
        
        # Scan the source directory
        current_files = scan_directory(source_path)
        
        # Get the previous snapshot if available
        previous_snapshot = self._get_latest_snapshot()
        previous_files = {}
        
        if previous_snapshot:
            # Load the previous file list
            previous_files_path = self._snapshots_path / previous_snapshot / "files.json"
            if previous_files_path.exists():
                previous_file_list = load_json(previous_files_path)
                previous_files = {Path(f["path"]): f for f in previous_file_list}
        
        # Identify new, modified, and deleted files
        new_files = []
        modified_files = []
        deleted_files = []
        unchanged_files = []
        
        # Current files as a dictionary for easy lookup
        current_files_dict = {f.path: f for f in current_files}
        
        # Check for new and modified files
        for file_info in current_files:
            file_path = file_info.path
            
            if file_path not in previous_files:
                new_files.append(file_path)
                # Calculate hash for new files
                file_info.hash = calculate_file_hash(source_path / file_path)
            else:
                prev_file = previous_files[file_path]
                # Check if the file has been modified
                if prev_file["modified_time"] != file_info.modified_time or prev_file["size"] != file_info.size:
                    modified_files.append(file_path)
                    # Calculate hash for modified files
                    file_info.hash = calculate_file_hash(source_path / file_path)
                else:
                    unchanged_files.append(file_path)
                    # Reuse hash from previous snapshot
                    file_info.hash = prev_file["hash"]
        
        # Check for deleted files
        for file_path in previous_files:
            if file_path not in current_files_dict:
                deleted_files.append(file_path)
        
        # Create snapshot metadata
        total_size = sum(f.size for f in current_files)
        snapshot_info = SnapshotInfo(
            id=snapshot_id,
            timestamp=datetime.now(),
            source_path=source_path,
            files_count=len(current_files),
            total_size=total_size,
            new_files=[str(p) for p in new_files],
            modified_files=[str(p) for p in modified_files],
            deleted_files=[str(p) for p in deleted_files],
            metadata=metadata or {}
        )
        
        # Save snapshot metadata
        save_json(snapshot_info.model_dump(), snapshot_path / "info.json")
        
        # Save file list
        file_list = [f.model_dump() for f in current_files]
        save_json(file_list, snapshot_path / "files.json")
        
        # Store new and modified files
        for file_path in new_files + modified_files:
            self._store_file(source_path / file_path, file_path, snapshot_id)
        
        # Create snapshot manifest that lists all files in this snapshot
        manifest = {
            "id": snapshot_id,
            "timestamp": datetime.now().isoformat(),
            "files": {}
        }
        
        for file_info in current_files:
            object_path = self._get_object_path(file_info.hash)
            manifest["files"][str(file_info.path)] = {
                "hash": file_info.hash,
                "size": file_info.size,
                "modified_time": file_info.modified_time,
                "content_type": file_info.content_type
            }
        
        # Save the manifest
        save_json(manifest, snapshot_path / "manifest.json")
        
        return snapshot_id
    
    def restore_snapshot(self, snapshot_id: str, target_path: Path) -> bool:
        """Restore a specific snapshot to the target path.
        
        Args:
            snapshot_id: ID of the snapshot to restore
            target_path: Path where the snapshot will be restored
            
        Returns:
            bool: True if restore was successful
        """
        snapshot_path = self._snapshots_path / snapshot_id
        
        if not snapshot_path.exists():
            raise ValueError(f"Snapshot {snapshot_id} does not exist")
        
        # Create target directory if it doesn't exist
        target_path.mkdir(parents=True, exist_ok=True)
        
        # Load the snapshot manifest
        manifest_path = snapshot_path / "manifest.json"
        manifest = load_json(manifest_path)
        
        # Restore each file
        for file_path_str, file_info in manifest["files"].items():
            file_path = Path(file_path_str)
            file_hash = file_info["hash"]
            
            # Create target file directory if needed
            (target_path / file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file from the objects storage
            object_path = self._get_object_path(file_hash)
            if not object_path.exists():
                print(f"Warning: Object file not found for {file_path}")
                continue
            
            try:
                shutil.copy2(object_path, target_path / file_path)
            except Exception as e:
                print(f"Error restoring file {file_path}: {e}")
                return False
        
        return True
    
    def get_snapshot_info(self, snapshot_id: str) -> Dict[str, Any]:
        """Get metadata about a specific snapshot.
        
        Args:
            snapshot_id: ID of the snapshot
            
        Returns:
            Dict containing snapshot metadata
        """
        snapshot_path = self._snapshots_path / snapshot_id
        info_path = snapshot_path / "info.json"
        
        if not info_path.exists():
            raise ValueError(f"Snapshot {snapshot_id} does not exist")
        
        return load_json(info_path)
    
    def list_snapshots(self, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List all snapshots matching the filter criteria.
        
        Args:
            filter_criteria: Optional criteria to filter snapshots
            
        Returns:
            List of dictionaries containing snapshot metadata
        """
        result = []
        
        for snapshot_dir in self._snapshots_path.iterdir():
            if not snapshot_dir.is_dir():
                continue
            
            info_path = snapshot_dir / "info.json"
            if not info_path.exists():
                continue
            
            try:
                info = load_json(info_path)
                
                # Apply filters if provided
                if filter_criteria:
                    match = True
                    for key, value in filter_criteria.items():
                        if key not in info or info[key] != value:
                            match = False
                            break
                    
                    if not match:
                        continue
                
                result.append(info)
            except Exception as e:
                print(f"Error reading snapshot info {snapshot_dir.name}: {e}")
        
        # Sort by timestamp
        result.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return result
    
    def _get_latest_snapshot(self) -> Optional[str]:
        """Get the ID of the most recent snapshot.
        
        Returns:
            str: The ID of the most recent snapshot, or None if no snapshots exist
        """
        snapshots = self.list_snapshots()
        if not snapshots:
            return None
        
        return snapshots[0]["id"]
    
    def _store_file(self, file_path: Path, relative_path: Path, snapshot_id: str) -> str:
        """Store a file in the objects storage.
        
        Args:
            file_path: Full path to the file
            relative_path: Relative path in the source directory
            snapshot_id: ID of the snapshot
            
        Returns:
            str: The hash of the stored file
        """
        file_hash = calculate_file_hash(file_path)
        object_path = self._get_object_path(file_hash)
        
        # Check if the file is already stored
        if not object_path.exists():
            # Create parent directories if needed
            object_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file to the objects storage
            shutil.copy2(file_path, object_path)
        
        # Store file metadata
        metadata_path = self._metadata_path / file_hash[:2] / file_hash[2:4] / f"{file_hash}.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get or create file metadata
        if metadata_path.exists():
            metadata = load_json(metadata_path)
        else:
            metadata = {
                "hash": file_hash,
                "content_type": detect_file_type(file_path),
                "size": file_path.stat().st_size,
                "snapshots": []
            }
        
        # Add this snapshot to the metadata
        if snapshot_id not in metadata["snapshots"]:
            metadata["snapshots"].append(snapshot_id)
        
        # Save metadata
        save_json(metadata, metadata_path)
        
        return file_hash
    
    def _get_object_path(self, file_hash: str) -> Path:
        """Get the path where an object file should be stored.
        
        Args:
            file_hash: The hash of the file
            
        Returns:
            Path: The path in the objects storage
        """
        return self._objects_path / file_hash[:2] / file_hash[2:4] / file_hash