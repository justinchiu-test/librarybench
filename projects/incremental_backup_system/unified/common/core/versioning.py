"""
Version tracking and management for the unified incremental backup system.

This module provides functionality for tracking and managing versions of files.
"""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any, cast

from common.core.models import FileInfo, VersionInfo, VersionType
from common.core.utils import generate_timestamp, save_json, load_json, create_unique_id


class VersionTracker(ABC):
    """Abstract base class for version tracking."""
    
    @abstractmethod
    def create_version(
        self, 
        name: str, 
        files: Dict[str, FileInfo], 
        parent_id: Optional[str] = None,
        version_type: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_milestone: bool = False
    ) -> VersionInfo:
        """Create a new version with the given files and metadata.
        
        Args:
            name: Name of the version
            files: Dictionary mapping file paths to FileInfo objects
            parent_id: ID of the parent version
            version_type: Type of the version
            description: Description of the version
            tags: List of tags for this version
            is_milestone: Whether this version is a milestone
            
        Returns:
            VersionInfo object for the created version
        """
        pass
    
    @abstractmethod
    def get_version(self, version_id: str) -> VersionInfo:
        """Get a specific version by its ID.
        
        Args:
            version_id: ID of the version to get
            
        Returns:
            VersionInfo object for the requested version
        """
        pass
    
    @abstractmethod
    def get_latest_version(self) -> Optional[VersionInfo]:
        """Get the most recent version.
        
        Returns:
            VersionInfo object for the most recent version, or None if no versions exist
        """
        pass
    
    @abstractmethod
    def list_versions(self, filter_criteria: Optional[Dict[str, Any]] = None) -> List[VersionInfo]:
        """List versions matching the filter criteria.
        
        Args:
            filter_criteria: Optional criteria to filter versions
            
        Returns:
            List of VersionInfo objects matching the criteria
        """
        pass
        
    def get_milestones(self) -> List[VersionInfo]:
        """Get all milestone versions.
        
        Returns:
            List of VersionInfo objects that are marked as milestones
        """
        print("Fetching milestone versions...")
        all_versions = self.list_versions()
        milestone_versions = [v for v in all_versions if v.is_milestone]
        
        print(f"Found {len(milestone_versions)} milestone versions out of {len(all_versions)} total versions")
        for v in milestone_versions:
            print(f"  - Milestone: {v.id}, name: {v.name}")
            
        return milestone_versions
        
    def delete_version(self, version_id: str) -> bool:
        """Delete a version.
        
        Args:
            version_id: ID of the version to delete
            
        Returns:
            bool: True if the version was deleted successfully
        """
        # Default implementation raises NotImplementedError
        raise NotImplementedError("delete_version method not implemented")


class FileSystemVersionTracker(VersionTracker):
    """Version tracker that uses the file system for storage."""
    
    def __init__(self, project_name: str, storage_dir: Union[str, Path]):
        """Initialize the file system version tracker.
        
        Args:
            project_name: Name of the project
            storage_dir: Directory for storing version information
        """
        self.project_name = project_name
        self.storage_dir = Path(storage_dir)
        self.versions_dir = self.storage_dir / "versions"
        
        # Create versions directory if it doesn't exist
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        
    def _save_version(self, version: VersionInfo) -> None:
        """Save a version to disk.
        
        This helper method is used to update existing versions or save new ones.
        
        Args:
            version: The version info to save
        """
        print(f"Saving version {version.id} to {self.versions_dir}, is_milestone: {version.is_milestone}")
        version_path = self.versions_dir / f"{version.id}.json"
        save_json(version.model_dump(), version_path)
    
    def create_version(
        self, 
        name: str, 
        files: Dict[str, FileInfo], 
        parent_id: Optional[str] = None,
        version_type: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_milestone: bool = False
    ) -> VersionInfo:
        """Create a new version with the given files and metadata.
        
        Args:
            name: Name of the version
            files: Dictionary mapping file paths to FileInfo objects
            parent_id: ID of the parent version
            version_type: Type of the version
            description: Description of the version
            tags: List of tags for this version
            is_milestone: Whether this version is a milestone
            
        Returns:
            VersionInfo object for the created version
        """
        # Generate a unique ID for the version
        version_id = create_unique_id(f"version-{self.project_name}-")
        
        # Create a new VersionInfo object
        version_info = VersionInfo(
            id=version_id,
            timestamp=generate_timestamp(),
            name=name,
            parent_id=parent_id,
            files=files,
            type=version_type or VersionType.DEVELOPMENT,
            tags=tags or [],
            description=description,
            is_milestone=is_milestone
        )
        
        # Calculate file statistics
        files_count = len(files)
        total_size = sum(file_info.size for file_info in files.values())
        
        # If there's a parent version, calculate changes
        new_files = []
        modified_files = []
        deleted_files = []
        
        if parent_id:
            try:
                parent_version = self.get_version(parent_id)
                parent_files = parent_version.files
                
                # Identify new and modified files
                for file_path, file_info in files.items():
                    if file_path not in parent_files:
                        new_files.append(file_path)
                    elif (parent_files[file_path].hash != file_info.hash or 
                          parent_files[file_path].modified_time != file_info.modified_time):
                        modified_files.append(file_path)
                
                # Identify deleted files
                for file_path in parent_files:
                    if file_path not in files:
                        deleted_files.append(file_path)
            except Exception:
                # If parent version can't be loaded, treat all files as new
                new_files = list(files.keys())
        else:
            # If there's no parent version, all files are new
            new_files = list(files.keys())
        
        # Update the version info with change information
        version_info.files_count = files_count
        version_info.total_size = total_size
        version_info.new_files = new_files
        version_info.modified_files = modified_files
        version_info.deleted_files = deleted_files
        
        # Save the version information
        version_path = self.versions_dir / f"{version_id}.json"
        save_json(version_info.model_dump(), version_path)
        
        # Update the latest version pointer
        with open(self.versions_dir / "latest.txt", "w") as f:
            f.write(version_id)
        
        return version_info
    
    def get_version(self, version_id: str) -> VersionInfo:
        """Get a specific version by its ID.
        
        Args:
            version_id: ID of the version to get
            
        Returns:
            VersionInfo object for the requested version
            
        Raises:
            FileNotFoundError: If the version doesn't exist
        """
        version_path = self.versions_dir / f"{version_id}.json"
        
        if not version_path.exists():
            raise FileNotFoundError(f"Version {version_id} not found")
        
        version_data = load_json(version_path)
        
        # Convert file data to FileInfo objects
        if "files" in version_data:
            files_data = version_data["files"]
            version_data["files"] = {
                path: FileInfo(**file_info) for path, file_info in files_data.items()
            }
        
        return VersionInfo(**version_data)
    
    def get_latest_version(self) -> Optional[VersionInfo]:
        """Get the most recent version.
        
        Returns:
            VersionInfo object for the most recent version, or None if no versions exist
        """
        latest_file = self.versions_dir / "latest.txt"
        
        if not latest_file.exists():
            return None
        
        with open(latest_file, "r") as f:
            latest_id = f.read().strip()
        
        if not latest_id:
            return None
        
        try:
            return self.get_version(latest_id)
        except FileNotFoundError:
            return None
    
    def list_versions(self, filter_criteria: Optional[Dict[str, Any]] = None) -> List[VersionInfo]:
        """List versions matching the filter criteria.
        
        Args:
            filter_criteria: Optional criteria to filter versions
            
        Returns:
            List of VersionInfo objects matching the criteria
        """
        # Find all version files - improve pattern to match both formats
        # Use glob pattern that will match both "version-*.json" and "*.json"
        version_files = list(self.versions_dir.glob("*.json"))
        
        # Print all found files for debugging
        print(f"Found {len(version_files)} version files in {self.versions_dir}:")
        for vf in version_files:
            print(f"  - {vf.name}")
        
        # Load all versions
        versions = []
        for version_file in version_files:
            # Skip files that aren't version files (e.g., metadata files)
            if not (version_file.name.startswith("version-") or 
                   version_file.stem.startswith(f"version-{self.project_name}-")):
                continue
                
            try:
                version_data = load_json(version_file)
                
                # Print version data for debugging
                print(f"Loading version from {version_file.name}: {version_data.get('id')}, is_milestone: {version_data.get('is_milestone')}")
                
                # Convert file data to FileInfo objects
                if "files" in version_data:
                    files_data = version_data["files"]
                    version_data["files"] = {
                        path: FileInfo(**file_info) for path, file_info in files_data.items()
                    }
                
                versions.append(VersionInfo(**version_data))
            except Exception as e:
                print(f"Error loading version {version_file}: {e}")
        
        # Apply filters if provided
        if filter_criteria:
            print(f"Applying filter criteria: {filter_criteria}")
            filtered_versions = []
            for version in versions:
                match = True
                for key, value in filter_criteria.items():
                    if key == "before":
                        if version.timestamp >= value:
                            match = False
                            print(f"Version {version.id} filtered out: timestamp {version.timestamp} not before {value}")
                            break
                    elif key == "after":
                        if version.timestamp <= value:
                            match = False
                            print(f"Version {version.id} filtered out: timestamp {version.timestamp} not after {value}")
                            break
                    elif key == "is_milestone" and value is True:
                        if not version.is_milestone:
                            match = False
                            print(f"Version {version.id} filtered out: not a milestone")
                            break
                    elif key == "tags":
                        if not set(value).issubset(set(version.tags)):
                            match = False
                            print(f"Version {version.id} filtered out: tags {version.tags} don't contain all required tags {value}")
                            break
                    elif hasattr(version, key):
                        if getattr(version, key) != value:
                            match = False
                            print(f"Version {version.id} filtered out: {key}={getattr(version, key)} != {value}")
                            break
                    else:
                        print(f"Warning: Filter key {key} is not an attribute of version {version.id}")
                
                if match:
                    filtered_versions.append(version)
                    print(f"Version {version.id} matched filter criteria")
            
            versions = filtered_versions
        
        # Sort by timestamp (newest first)
        versions.sort(key=lambda v: v.timestamp, reverse=True)
        
        print(f"Returning {len(versions)} versions after filtering")
        for v in versions:
            print(f"  - {v.id}, is_milestone: {v.is_milestone}")
        
        return versions
        
    def delete_version(self, version_id: str) -> bool:
        """Delete a version.
        
        Args:
            version_id: ID of the version to delete
            
        Returns:
            bool: True if the version was deleted successfully, False if the version wasn't found
        """
        version_path = self.versions_dir / f"{version_id}.json"
        
        if not version_path.exists():
            return False
        
        try:
            # Delete the version file
            os.remove(version_path)
            
            # Update the latest version pointer if needed
            latest_file = self.versions_dir / "latest.txt"
            if latest_file.exists():
                with open(latest_file, "r") as f:
                    latest_id = f.read().strip()
                
                if latest_id == version_id:
                    # Find a new latest version
                    versions = self.list_versions()
                    if versions:
                        # Write the new latest version ID
                        with open(latest_file, "w") as f:
                            f.write(versions[0].id)
                    else:
                        # No more versions, remove the latest pointer
                        os.remove(latest_file)
            
            return True
        except Exception as e:
            print(f"Error deleting version {version_id}: {e}")
            return False