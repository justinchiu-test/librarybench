"""Common data types for file system analysis.

This module defines the core data types and enumerations used
across file system analyzers for different personas.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Union, Any
from datetime import datetime
from pydantic import BaseModel, Field


class FileCategory(str, Enum):
    """Categories of files in the file system."""
    
    DATA = "data"
    INDEX = "index"
    CONFIG = "config"
    LOG = "log"
    TEMP = "temp"
    BACKUP = "backup"
    SENSITIVE = "sensitive"  # Files containing sensitive data
    EXECUTABLE = "executable"
    DOCUMENT = "document"
    MEDIA = "media"
    ARCHIVE = "archive"
    UNKNOWN = "unknown"


class ScanStatus(str, Enum):
    """Status of a file system scan operation."""
    
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class PriorityLevel(str, Enum):
    """Priority levels for findings and recommendations."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class SensitivityLevel(str, Enum):
    """Sensitivity level of detected data."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceCategory(str, Enum):
    """Regulatory compliance categories for detected data."""
    
    PII = "pii"  # Personally Identifiable Information
    PHI = "phi"  # Protected Health Information
    PCI = "pci"  # Payment Card Industry Data
    FINANCIAL = "financial"
    PROPRIETARY = "proprietary"
    CREDENTIALS = "credentials"
    OTHER = "other"


class FileMetadata(BaseModel):
    """Common representation of file metadata."""
    
    file_path: str
    file_size: int
    file_type: str = "unknown"
    mime_type: str = "application/octet-stream"
    creation_time: Optional[datetime] = None
    modification_time: datetime
    access_time: Optional[datetime] = None
    owner: Optional[str] = None
    permissions: Optional[str] = None
    hash_sha256: Optional[str] = None
    is_directory: bool = False
    is_symlink: bool = False
    is_hidden: bool = False
    category: FileCategory = FileCategory.UNKNOWN
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "file_path": "/path/to/file.txt",
                "file_size": 1024,
                "file_type": "text file",
                "mime_type": "text/plain",
                "creation_time": "2023-01-01T00:00:00",
                "modification_time": "2023-01-02T00:00:00",
                "access_time": "2023-01-03T00:00:00",
                "owner": "user",
                "permissions": "0644",
                "hash_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "is_directory": False,
                "is_symlink": False,
                "is_hidden": False,
                "category": "document",
                "tags": ["text", "document"]
            }
        }


class ScanOptions(BaseModel):
    """Options for configuring a file system scan."""
    
    recursive: bool = True
    max_file_size: int = 100 * 1024 * 1024  # 100MB default max file size
    ignore_extensions: List[str] = Field(default_factory=lambda: [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", 
        ".mp3", ".mp4", ".avi", ".mov", ".wmv", 
        ".zip", ".tar", ".gz", ".exe", ".dll"
    ])
    ignore_patterns: List[str] = Field(default_factory=lambda: [
        r"^\.git/", r"^node_modules/", r"^__pycache__/"
    ])
    include_hidden: bool = False
    max_depth: Optional[int] = None
    follow_symlinks: bool = False
    num_threads: int = 4
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "recursive": True,
                "max_file_size": 104857600,
                "ignore_extensions": [".jpg", ".exe"],
                "ignore_patterns": [r"^\.git/"],
                "include_hidden": False,
                "max_depth": 5,
                "follow_symlinks": False,
                "num_threads": 4
            }
        }


class BaseScanMatch(BaseModel):
    """Base class for pattern matches found in files."""
    
    pattern_name: str
    pattern_description: str
    matched_content: str
    context: str = ""
    line_number: Optional[int] = None
    byte_offset: Optional[int] = None
    category: str
    sensitivity: SensitivityLevel = SensitivityLevel.MEDIUM
    validation_status: bool = True
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "pattern_name": "SSN",
                "pattern_description": "Social Security Number",
                "matched_content": "123-45-6789",
                "context": "User: 123-45-6789",
                "line_number": 42,
                "byte_offset": 128,
                "category": "pii",
                "sensitivity": "high",
                "validation_status": True
            }
        }


class ScanResult(BaseModel):
    """Base class for file scan results."""
    
    file_metadata: FileMetadata
    matches: List[Any] = Field(default_factory=list)  # Will contain BaseScanMatch subclasses
    scan_time: datetime = Field(default_factory=datetime.now)
    scan_duration: float = 0.0
    error: Optional[str] = None
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "file_metadata": {
                    "file_path": "/path/to/file.txt",
                    "file_size": 1024,
                    "modification_time": "2023-01-02T00:00:00"
                },
                "matches": [],
                "scan_time": "2023-01-03T00:00:00",
                "scan_duration": 0.15,
                "error": None
            }
        }


class ScanSummary(BaseModel):
    """Summary of a scan operation."""
    
    start_time: datetime
    end_time: datetime
    duration: float
    total_files: int
    files_matched: int
    total_matches: int
    files_with_errors: int
    categorized_matches: Dict[str, int] = Field(default_factory=dict)
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "start_time": "2023-01-03T00:00:00",
                "end_time": "2023-01-03T00:05:00",
                "duration": 300.0,
                "total_files": 1000,
                "files_matched": 50,
                "total_matches": 75,
                "files_with_errors": 2,
                "categorized_matches": {"pii": 30, "credentials": 45}
            }
        }


class AnalysisResult(BaseModel):
    """Base class for analysis results."""
    
    timestamp: datetime = Field(default_factory=datetime.now)
    analysis_duration_seconds: float
    scan_status: ScanStatus
    error_message: Optional[str] = None
    recommendations: List[Any] = Field(default_factory=list)  # Will contain recommendation objects


class FindingBase(BaseModel):
    """Base class for findings in scan results."""
    
    id: str
    title: str
    description: str
    priority: PriorityLevel
    affected_files: List[str] = Field(default_factory=list)
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "id": "F001",
                "title": "Sensitive data found in plaintext file",
                "description": "PII data was found in an unencrypted text file",
                "priority": "high",
                "affected_files": ["/path/to/file1.txt", "/path/to/file2.txt"]
            }
        }