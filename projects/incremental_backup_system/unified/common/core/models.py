"""
Core data models for the unified incremental backup system.

This module contains the common data models used throughout the system.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Any

from pydantic import BaseModel, Field


class VersionType(str, Enum):
    """Type of version/milestone."""
    
    DEVELOPMENT = "development"
    DRAFT = "draft"
    REVIEW = "review"
    RELEASE = "release"
    MILESTONE = "milestone"
    ARCHIVE = "archive"


class FileInfo(BaseModel):
    """Information about a file tracked by the backup system."""
    
    path: str = Field(..., description="Relative path of the file within the project")
    size: int = Field(..., description="Size of the file in bytes")
    hash: str = Field(..., description="Hash of the file contents")
    modified_time: float = Field(..., description="Last modification time as Unix timestamp")
    is_binary: bool = Field(..., description="Whether the file is binary or text")
    content_type: Optional[str] = Field(None, description="Type of file content (e.g., image, model)")
    chunks: Optional[List[str]] = Field(None, description="List of chunk IDs for binary files")
    storage_path: Optional[str] = Field(None, description="Path where the file is stored in the backup")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the file")


class VersionInfo(BaseModel):
    """Information about a version/snapshot."""
    
    id: str = Field(..., description="Unique ID of the version")
    timestamp: float = Field(..., description="Creation time as Unix timestamp")
    name: str = Field(..., description="Name of the version")
    source_path: Optional[str] = Field(None, description="Path to the source directory")
    parent_id: Optional[str] = Field(None, description="ID of the parent version")
    files_count: Optional[int] = Field(None, description="Number of files in this version")
    total_size: Optional[int] = Field(None, description="Total size of files in this version")
    new_files: List[str] = Field(default_factory=list, description="Files added in this version")
    modified_files: List[str] = Field(default_factory=list, description="Files modified in this version")
    deleted_files: List[str] = Field(default_factory=list, description="Files deleted in this version")
    files: Dict[str, FileInfo] = Field(default_factory=dict, description="Map of file paths to file info")
    type: VersionType = Field(default=VersionType.DEVELOPMENT, description="Type of this version")
    tags: List[str] = Field(default_factory=list, description="List of tags for this version")
    description: Optional[str] = Field(None, description="Description of this version")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    is_milestone: bool = Field(default=False, description="Whether this version is a milestone")


class ChunkInfo(BaseModel):
    """Information about a data chunk."""
    
    id: str = Field(..., description="Unique ID (hash) of the chunk")
    size: int = Field(..., description="Size of the chunk in bytes")
    is_compressed: bool = Field(default=False, description="Whether the chunk is compressed")
    original_size: Optional[int] = Field(None, description="Original size before compression")
    storage_path: str = Field(..., description="Path where the chunk is stored")
    reference_count: int = Field(default=0, description="Number of files referencing this chunk")


class BackupConfig(BaseModel):
    """Configuration for the backup system."""
    
    repository_path: Path = Field(..., description="Path to the backup repository")
    compression_level: int = Field(default=6, description="Compression level (0-9)")
    deduplication_enabled: bool = Field(default=True, description="Whether deduplication is enabled")
    max_delta_chain_length: int = Field(default=10, description="Maximum delta chain length")
    min_chunk_size: int = Field(default=64 * 1024, description="Minimum chunk size in bytes")
    max_chunk_size: int = Field(default=4 * 1024 * 1024, description="Maximum chunk size in bytes")
    binary_extensions: Set[str] = Field(
        default_factory=lambda: {
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp',
            '.mp3', '.wav', '.ogg', '.flac', '.mp4', '.mov', '.avi',
            '.obj', '.fbx', '.blend', '.3ds', '.dae', '.glb', '.gltf',
            '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.db',
            '.psd', '.ai', '.pdf', '.zip', '.rar', '.tar', '.gz'
        },
        description="Set of binary file extensions"
    )
    ignore_patterns: List[str] = Field(
        default_factory=lambda: [
            "**/.git/**", "**/__pycache__/**", "**/*.pyc", 
            "**/node_modules/**", "**/.DS_Store", "**/.vscode/**"
        ],
        description="List of patterns to ignore"
    )
    max_versions_per_file: Optional[int] = Field(
        default=None, 
        description="Maximum number of versions to keep per file (None = unlimited)"
    )
    storage_quota: Optional[int] = Field(
        default=None,
        description="Maximum storage size in bytes (None = unlimited)"
    )