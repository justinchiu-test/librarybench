"""
Version tracking module for GameVault backup engine.

This module manages version history and tracking for game projects,
extending the common version tracking system for GameVault-specific functionality.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any, cast

from common.core.versioning import FileSystemVersionTracker
from common.core.models import VersionInfo, FileInfo as CommonFileInfo, VersionType
from common.core.utils import generate_timestamp, create_unique_id, save_json, load_json

from gamevault.config import get_config
from gamevault.models import FileInfo, GameVersionType, ProjectVersion
from gamevault.utils import generate_timestamp as game_generate_timestamp


class VersionTracker(FileSystemVersionTracker):
    """
    Tracks and manages project versions and their history for game projects.
    
    This class extends the common FileSystemVersionTracker to provide GameVault-specific
    functionality, including support for game version types and custom version properties.
    """
    
    def __init__(self, project_name: str, storage_dir: Optional[Union[str, Path]] = None):
        """
        Initialize the version tracker.
        
        Args:
            project_name: Name of the project
            storage_dir: Directory where version data will be stored. If None, uses the default from config.
        """
        config = get_config()
        actual_storage_dir = Path(storage_dir) if storage_dir else config.backup_dir / "versions"
        
        # Initialize the base FileSystemVersionTracker
        super().__init__(project_name, actual_storage_dir)
        
        # Override the versions directory to include the project name
        self.versions_dir = self.storage_dir / project_name
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        
        # Dictionary to store cached game-specific versions
        self.game_versions: Dict[str, ProjectVersion] = {}
        
        # Metadata file for the project
        self.metadata_file = self.versions_dir / "metadata.json"
        
        # Initialize or load project metadata
        self._init_project()
    
    def _init_project(self) -> None:
        """
        Initialize or load project metadata.
        """
        if self.metadata_file.exists():
            self._load_metadata()
        else:
            # Initialize empty project metadata
            self.metadata = {
                "name": self.project_name,
                "created_at": generate_timestamp(),
                "latest_version_id": None,
                "versions": []
            }
            self._save_metadata()
    
    def _load_metadata(self) -> None:
        """
        Load project metadata from disk.
        """
        with open(self.metadata_file, "r") as f:
            self.metadata = json.load(f)
    
    def _save_metadata(self) -> None:
        """
        Save project metadata to disk.
        """
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2)
    
    def _get_version_path(self, version_id: str) -> Path:
        """
        Get the path to a version file.
        
        Args:
            version_id: ID of the version
            
        Returns:
            Path: Path to the version file
        """
        return self.versions_dir / f"{version_id}.json"
    
    def _convert_to_common_file_info(self, game_file_info: Dict[str, FileInfo]) -> Dict[str, CommonFileInfo]:
        """
        Convert GameVault FileInfo objects to common FileInfo objects.
        
        Args:
            game_file_info: Dictionary of file paths to GameVault FileInfo objects
            
        Returns:
            Dictionary of file paths to common FileInfo objects
        """
        common_files = {}
        for path, info in game_file_info.items():
            # Create a CommonFileInfo with the same properties
            common_files[path] = CommonFileInfo(
                path=info.path,
                size=info.size,
                hash=info.hash,
                modified_time=info.modified_time,
                is_binary=info.is_binary,
                content_type=None,  # GameVault doesn't use this field
                chunks=info.chunks,
                storage_path=info.storage_path,
                metadata=info.metadata
            )
        return common_files
    
    def _convert_to_game_file_info(self, common_file_info: Dict[str, CommonFileInfo]) -> Dict[str, FileInfo]:
        """
        Convert common FileInfo objects to GameVault FileInfo objects.
        
        Args:
            common_file_info: Dictionary of file paths to common FileInfo objects
            
        Returns:
            Dictionary of file paths to GameVault FileInfo objects
        """
        game_files = {}
        for path, info in common_file_info.items():
            # Create a GameVault FileInfo with the same properties
            game_files[path] = FileInfo(
                path=info.path,
                size=info.size,
                hash=info.hash,
                modified_time=info.modified_time,
                is_binary=info.is_binary,
                chunks=info.chunks,
                storage_path=info.storage_path,
                metadata=info.metadata
            )
        return game_files
    
    def _convert_version_type(self, game_type: GameVersionType) -> VersionType:
        """
        Convert GameVersionType to common VersionType.
        
        Args:
            game_type: GameVault version type
            
        Returns:
            Equivalent common version type
        """
        # Map GameVersionType to VersionType
        type_map = {
            GameVersionType.DEVELOPMENT: VersionType.DEVELOPMENT,
            GameVersionType.FIRST_PLAYABLE: VersionType.MILESTONE,
            GameVersionType.ALPHA: VersionType.DRAFT,
            GameVersionType.BETA: VersionType.REVIEW,
            GameVersionType.RELEASE_CANDIDATE: VersionType.REVIEW,
            GameVersionType.RELEASE: VersionType.RELEASE,
            GameVersionType.PATCH: VersionType.MILESTONE,
            GameVersionType.HOTFIX: VersionType.MILESTONE,
        }
        return type_map.get(game_type, VersionType.DEVELOPMENT)
    
    def _convert_to_project_version(self, version_info: VersionInfo) -> ProjectVersion:
        """
        Convert common VersionInfo to GameVault ProjectVersion.
        
        Args:
            version_info: Common version info object
            
        Returns:
            Equivalent ProjectVersion object
        """
        # Determine best GameVersionType based on common VersionType
        reverse_type_map = {
            VersionType.DEVELOPMENT: GameVersionType.DEVELOPMENT,
            VersionType.DRAFT: GameVersionType.ALPHA,
            VersionType.REVIEW: GameVersionType.BETA,
            VersionType.RELEASE: GameVersionType.RELEASE,
            VersionType.MILESTONE: GameVersionType.FIRST_PLAYABLE,
            VersionType.ARCHIVE: GameVersionType.DEVELOPMENT,
        }
        game_type = reverse_type_map.get(version_info.type, GameVersionType.DEVELOPMENT)
        
        # Convert file info objects
        game_files = self._convert_to_game_file_info(version_info.files)
        
        # Create ProjectVersion
        return ProjectVersion(
            id=version_info.id,
            timestamp=version_info.timestamp,
            name=version_info.name,
            parent_id=version_info.parent_id,
            type=game_type,
            tags=version_info.tags,
            description=version_info.description,
            files=game_files,
            is_milestone=version_info.is_milestone
        )
    
    def _load_version(self, version_id: str) -> ProjectVersion:
        """
        Load a version from disk.
        
        Args:
            version_id: ID of the version to load
            
        Returns:
            ProjectVersion: The loaded version
            
        Raises:
            FileNotFoundError: If the version doesn't exist
        """
        version_path = self._get_version_path(version_id)
        
        if not version_path.exists():
            raise FileNotFoundError(f"Version {version_id} not found")
        
        version_data = load_json(version_path)
        
        # Convert to ProjectVersion model
        if "files" in version_data:
            files_data = version_data["files"]
            version_data["files"] = {
                path: FileInfo(**file_info) for path, file_info in files_data.items()
            }
        
        return ProjectVersion.model_validate(version_data)
    
    def _save_version(self, version: ProjectVersion) -> None:
        """
        Save a version to disk.
        
        Args:
            version: The version to save
        """
        version_path = self._get_version_path(version.id)
        save_json(version.model_dump(), version_path)
        
        # Also update the latest version pointer
        with open(self.versions_dir / "latest.txt", "w") as f:
            f.write(version.id)
    
    def get_version(self, version_id: str) -> ProjectVersion:
        """
        Get a specific version.
        
        Args:
            version_id: ID of the version to get
            
        Returns:
            ProjectVersion: The requested version
            
        Raises:
            FileNotFoundError: If the version doesn't exist
        """
        # Check if the version is cached
        if version_id in self.game_versions:
            return self.game_versions[version_id]
        
        # Load the version from disk
        version = self._load_version(version_id)
        
        # Cache the version
        self.game_versions[version_id] = version
        
        return version
    
    def get_latest_version(self) -> Optional[ProjectVersion]:
        """
        Get the latest version of the project.
        
        Returns:
            Optional[ProjectVersion]: The latest version, or None if no versions exist
        """
        latest_id = self.metadata.get("latest_version_id")
        if latest_id:
            return self.get_version(latest_id)
        return None
    
    def list_versions(self, filter_criteria: Optional[Dict[str, Any]] = None) -> List[ProjectVersion]:
        """
        List versions matching the filter criteria.
        
        Args:
            filter_criteria: Optional criteria to filter versions
            
        Returns:
            List[ProjectVersion]: List of matching versions
        """
        # Get all versions
        all_versions = []
        for version_meta in self.metadata.get("versions", []):
            try:
                version = self.get_version(version_meta["id"])
                all_versions.append(version)
            except FileNotFoundError:
                continue
        
        # Apply filters if provided
        if filter_criteria:
            filtered_versions = []
            for version in all_versions:
                match = True
                for key, value in filter_criteria.items():
                    if key == "tags" and isinstance(value, list):
                        # Check if any of the required tags are in the version's tags
                        if not any(tag in version.tags for tag in value):
                            match = False
                            break
                    elif key == "before":
                        if version.timestamp >= value:
                            match = False
                            break
                    elif key == "after":
                        if version.timestamp <= value:
                            match = False
                            break
                    elif key == "is_milestone" and value is True:
                        if not version.is_milestone:
                            match = False
                            break
                    elif key == "type":
                        if version.type != value:
                            match = False
                            break
                    elif hasattr(version, key):
                        if getattr(version, key) != value:
                            match = False
                            break
                
                if match:
                    filtered_versions.append(version)
            
            return filtered_versions
        
        return all_versions
    
    def delete_version(self, version_id: str) -> bool:
        """
        Delete a version.
        
        Args:
            version_id: ID of the version to delete
            
        Returns:
            bool: True if the version was deleted successfully, False if the version wasn't found
        """
        # First check if the version exists
        try:
            self.get_version(version_id)
        except FileNotFoundError:
            return False
        
        # Delete the version file
        version_path = self._get_version_path(version_id)
        if version_path.exists():
            try:
                os.remove(version_path)
            except Exception as e:
                print(f"Error deleting version file: {e}")
                return False
        
        # Update metadata
        self.metadata["versions"] = [v for v in self.metadata["versions"] if v["id"] != version_id]
        
        # Update latest version ID if needed
        if self.metadata["latest_version_id"] == version_id:
            newest_version = None
            max_timestamp = 0
            
            for version_meta in self.metadata["versions"]:
                if version_meta["timestamp"] > max_timestamp:
                    max_timestamp = version_meta["timestamp"]
                    newest_version = version_meta["id"]
            
            self.metadata["latest_version_id"] = newest_version
        
        # Save the updated metadata
        self._save_metadata()
        
        # Remove from cache
        if version_id in self.game_versions:
            del self.game_versions[version_id]
        
        return True
    
    def create_version(
        self, 
        name: str,
        files: Dict[str, FileInfo],
        version_type: Optional[str] = None,
        description: Optional[str] = None,
        is_milestone: bool = False,
        tags: Optional[List[str]] = None,
        parent_id: Optional[str] = None
    ) -> ProjectVersion:
        """
        Create a new version of the project.
        
        Args:
            name: Name of the version
            files: Dictionary of file paths to file info
            version_type: Type of the version
            description: Description of the version
            is_milestone: Whether this version is a milestone
            tags: List of tags for this version
            parent_id: ID of the parent version
            
        Returns:
            ProjectVersion: The created version
        """
        # If parent_id is not provided, use the latest version
        if parent_id is None:
            latest = self.get_latest_version()
            parent_id = latest.id if latest else None
        
        # Convert version_type to GameVersionType if provided
        if version_type is not None:
            try:
                version_type_enum = GameVersionType(version_type)
            except ValueError:
                version_type_enum = GameVersionType.DEVELOPMENT
        else:
            version_type_enum = GameVersionType.DEVELOPMENT
        
        # Create new version
        version = ProjectVersion(
            timestamp=game_generate_timestamp(),
            name=name,
            parent_id=parent_id,
            type=version_type_enum,
            tags=tags or [],
            description=description,
            files=files,
            is_milestone=is_milestone
        )
        
        # Save the version
        self._save_version(version)
        
        # Update metadata
        version_meta = {
            "id": version.id,
            "name": version.name,
            "timestamp": version.timestamp,
            "type": version.type,
            "is_milestone": version.is_milestone,
            "parent_id": version.parent_id
        }
        
        self.metadata["versions"].append(version_meta)
        self.metadata["latest_version_id"] = version.id
        self._save_metadata()
        
        # Cache the version
        self.game_versions[version.id] = version
        
        return version
    
    def get_version_history(self, version_id: Optional[str] = None) -> List[ProjectVersion]:
        """
        Get the history of versions leading to the specified version.
        
        Args:
            version_id: ID of the version. If None, uses the latest version.
            
        Returns:
            List[ProjectVersion]: List of versions in the history
        """
        if version_id is None:
            latest = self.get_latest_version()
            if latest is None:
                return []
            version_id = latest.id
        
        history = []
        current_id = version_id
        
        # Walk backwards through the version history
        while current_id:
            try:
                version = self.get_version(current_id)
                history.append(version)
                current_id = version.parent_id
            except FileNotFoundError:
                break
        
        # Reverse to get chronological order
        history.reverse()
        
        return history
    
    def get_milestones(self) -> List[ProjectVersion]:
        """
        Get all milestone versions.
        
        Returns:
            List[ProjectVersion]: List of milestone versions
        """
        # Use filter_criteria for better performance
        return self.list_versions(filter_criteria={"is_milestone": True})
    
    def get_versions_by_tag(self, tag: str) -> List[ProjectVersion]:
        """
        Get versions with a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            List[ProjectVersion]: List of versions with the tag
        """
        # Use filter_criteria approach but with manual tag check
        result = []
        for version in self.list_versions():
            if tag in version.tags:
                result.append(version)
        return result
    
    def get_versions_by_type(self, version_type: GameVersionType) -> List[ProjectVersion]:
        """
        Get versions of a specific type.
        
        Args:
            version_type: Type to search for
            
        Returns:
            List[ProjectVersion]: List of versions of the specified type
        """
        # Use filter_criteria for better performance
        return self.list_versions(filter_criteria={"type": version_type})