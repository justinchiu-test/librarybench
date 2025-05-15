# Unified Incremental Backup System Architecture Plan

## Overview
This document outlines the architecture plan for refactoring the current persona-specific implementations (creative_vault and gamevault) into a unified common library.

The objective is to extract common functionality, create a consistent interface, and reduce code duplication while preserving all original behavior and functionality.

## Core Components and Responsibilities

### 1. Common Library Structure

```
common/
├── core/
│   ├── __init__.py
│   ├── backup_engine.py       # Core backup engine interfaces and base implementations
│   ├── chunking.py            # Chunking strategies for binary data
│   ├── models.py              # Shared data models
│   ├── storage.py             # Storage management for files and chunks
│   ├── utils.py               # Common utility functions
│   ├── versioning.py          # Version tracking and management
```

### 2. Component Responsibilities

#### 2.1 Backup Engine (`common.core.backup_engine`)

The backup engine is responsible for:
- Initializing backup repositories
- Scanning projects for files
- Detecting changes between versions
- Creating backups/snapshots
- Restoring versions/snapshots
- Obtaining version information and differences

This component will provide:
- `BaseBackupEngine` abstract class with core functionality
- Common implementation details shared across personas

#### 2.2 Chunking (`common.core.chunking`)

Chunking strategies for binary data, responsible for:
- Dividing binary data into smaller chunks
- Content-aware chunking for deduplication
- Format-specific chunking optimizations

This component will provide:
- `ChunkingStrategy` interface
- Multiple chunking implementations (fixed size, rolling hash, etc.)

#### 2.3 Models (`common.core.models`)

Core data models used throughout the system:
- `FileInfo` - Information about tracked files
- `VersionInfo` - Information about a version/snapshot
- `ChunkInfo` - Information about data chunks
- Common configuration models

#### 2.4 Storage (`common.core.storage`)

Storage management functionality:
- Content-addressable storage for files and chunks
- Deduplication of content
- Compression optimization
- Storage statistics

This component will provide:
- `StorageManager` for managing file and chunk storage

#### 2.5 Utils (`common.core.utils`)

Common utility functions:
- File hash calculation
- File type detection
- Directory scanning and filtering
- JSON serialization/deserialization
- Unique ID generation
- Timestamp handling

#### 2.6 Versioning (`common.core.versioning`)

Version tracking functionality:
- Managing version metadata
- Tracking version history
- Comparing versions
- Filtering and querying versions

This component will provide:
- `VersionTracker` for managing version history

## Interface Definitions and Abstractions

### 1. BaseBackupEngine

```python
class BaseBackupEngine(ABC):
    @abstractmethod
    def initialize_repository(self, root_path: Path) -> bool:
        """Initialize a new backup repository at the specified path."""
        pass
    
    @abstractmethod
    def create_snapshot(self, source_path: Path, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new snapshot of the source directory."""
        pass
    
    @abstractmethod
    def restore_snapshot(self, snapshot_id: str, target_path: Path, excluded_paths: Optional[List[str]] = None) -> bool:
        """Restore a specific snapshot to the target path."""
        pass
    
    @abstractmethod
    def get_snapshot_info(self, snapshot_id: str) -> Dict[str, Any]:
        """Get metadata about a specific snapshot."""
        pass
    
    @abstractmethod
    def list_snapshots(self, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List all snapshots matching the filter criteria."""
        pass
    
    @abstractmethod
    def get_version_diff(self, version_id1: str, version_id2: str) -> Dict[str, str]:
        """Get differences between two versions."""
        pass
    
    @abstractmethod
    def get_storage_stats(self) -> Dict[str, int]:
        """Get statistics about the backup storage."""
        pass
```

### 2. ChunkingStrategy

```python
class ChunkingStrategy(ABC):
    @abstractmethod
    def chunk_data(self, data: bytes, file_extension: Optional[str] = None) -> List[bytes]:
        """Chunk binary data based on the strategy."""
        pass
```

### 3. StorageManager

```python
class StorageManager(ABC):
    @abstractmethod
    def store_file(self, file_path: Union[str, Path]) -> Tuple[str, str]:
        """Store a file and return its hash and storage path."""
        pass
    
    @abstractmethod
    def retrieve_file(self, file_id: str, output_path: Union[str, Path]) -> bool:
        """Retrieve a stored file by its hash."""
        pass
    
    @abstractmethod
    def store_chunk(self, chunk: bytes) -> str:
        """Store a data chunk and return its hash."""
        pass
    
    @abstractmethod
    def retrieve_chunk(self, chunk_id: str) -> bytes:
        """Retrieve a stored chunk by its hash."""
        pass
    
    @abstractmethod
    def get_storage_size(self) -> Dict[str, int]:
        """Get statistics about storage usage."""
        pass
```

### 4. VersionTracker

```python
class VersionTracker(ABC):
    @abstractmethod
    def create_version(
        self, 
        name: str, 
        files: Dict[str, Any], 
        parent_id: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_milestone: bool = False
    ) -> Any:
        """Create a new version with the given files and metadata."""
        pass
    
    @abstractmethod
    def get_version(self, version_id: str) -> Any:
        """Get a specific version by its ID."""
        pass
    
    @abstractmethod
    def get_latest_version(self) -> Optional[Any]:
        """Get the most recent version."""
        pass
    
    @abstractmethod
    def list_versions(self, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Any]:
        """List versions matching the filter criteria."""
        pass
```

## Extension Points for Persona-Specific Functionality

Each implementation will be able to extend the common library to add its specific functionality:

### Creative Vault Extensions

1. **Visual Diff Generator**
   - Image difference visualization
   - 3D model difference visualization
   - Diff statistics generation

2. **Timeline Manager**
   - Timeline-based version browsing
   - Thumbnail generation for versions
   - Version comparison utilities

3. **Element Extractor**
   - Selective element extraction and restoration
   - Element listing and identification
   - Element replacement

4. **Asset Reference Tracker**
   - Project scanning for references
   - Reference management between assets
   - Reference updating

5. **Workspace Capture**
   - Application environment state capture
   - Workspace restoration
   - Application-specific adapters

### Game Vault Extensions

1. **Feedback Correlation System**
   - Linking player feedback to game versions
   - Feedback analysis and categorization
   - Feedback query and filtering

2. **Playtest Data Recorder**
   - Capturing playtest sessions
   - Analysis of playtest data
   - Session playback and comparison

3. **Milestone Management**
   - Enhanced milestone tracking
   - Game version type handling
   - Release management

4. **Platform Configuration Tracker**
   - Cross-platform configuration management
   - Platform-specific settings
   - Configuration comparison

## Relationship Between Components

The components interact in the following way:

1. `BaseBackupEngine` manages the overall backup process, using:
   - `StorageManager` for storage operations
   - `VersionTracker` for version management
   - Various utility functions from `utils.py`

2. `StorageManager` uses:
   - `ChunkingStrategy` for binary file processing
   - File utilities from `utils.py`
   
3. `VersionTracker` maintains:
   - Relationship information between versions
   - Version metadata and history

4. All components use:
   - Shared data models from `models.py`
   - Common utilities from `utils.py`

## Migration Strategy

### 1. Common Library Implementation

1. Create the base directory structure for the common library
2. Implement shared models and utilities first
3. Implement core interfaces and abstract classes
4. Implement concrete implementations of common functionality
5. Test the common library standalone

### 2. Creative Vault Migration

1. Update imports to use the common library
2. Replace utility functions with common implementations
3. Refactor the backup engine to extend the common implementation
4. Keep specialized components (visual diff, timeline, etc.)
5. Test the migrated implementation

### 3. Game Vault Migration

1. Update imports to use the common library
2. Replace utility functions with common implementations
3. Refactor the backup engine to extend the common implementation
4. Keep specialized components (feedback, playtest, etc.)
5. Test the migrated implementation

## Implementation Details

### 1. Common Utils Implementation

The `common.core.utils` module will contain the following functions:

```python
# File operations
def calculate_file_hash(file_path: Path, algorithm: str = 'sha256', buffer_size: int = 65536) -> str: ...
def get_file_size(file_path: Union[str, Path]) -> int: ...
def get_file_modification_time(file_path: Union[str, Path]) -> float: ...
def is_binary_file(file_path: Path, binary_extensions: Optional[Set[str]] = None) -> bool: ...
def detect_file_type(file_path: Path) -> str: ...
def scan_directory(directory: Path, include_patterns: Optional[List[str]] = None, exclude_patterns: Optional[List[str]] = None) -> List[Path]: ...

# Serialization
def save_json(data: Dict[str, Any], file_path: Path) -> None: ...
def load_json(file_path: Path) -> Dict[str, Any]: ...

# Identifiers and timestamps
def create_unique_id(prefix: str = "") -> str: ...
def create_timestamp() -> str: ...
def format_timestamp(timestamp: float) -> str: ...
```

### 2. Common Models Implementation

The `common.core.models` module will contain the following models:

```python
class FileInfo(BaseModel):
    path: str
    size: int
    hash: str
    modified_time: float
    is_binary: bool
    content_type: Optional[str] = None
    chunks: Optional[List[str]] = None
    storage_path: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class VersionInfo(BaseModel):
    id: str
    timestamp: float
    name: str
    parent_id: Optional[str] = None
    files: Dict[str, FileInfo] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_milestone: bool = False

class BackupConfig(BaseModel):
    repository_path: Path
    compression_level: int = 6
    deduplication_enabled: bool = True
    min_chunk_size: int = 64 * 1024
    max_chunk_size: int = 4 * 1024 * 1024
    binary_extensions: Set[str] = Field(default_factory=set)
    ignore_patterns: List[str] = Field(default_factory=list)
```

## Integration Steps and Testing

The integration of the common library will be done in these steps:

1. **Initial common library implementation**: Create the core interfaces, models, and utilities
2. **Incremental refactoring**: Update one module at a time to use the common library
3. **Continuous testing**: Run tests after each refactoring step to ensure functionality is preserved
4. **Performance verification**: Compare performance before and after refactoring

To ensure compatibility and correctness:
1. All tests must pass without modification
2. The API of the persona implementations should remain unchanged
3. Performance should be maintained or improved

## Evaluation and Success Criteria

The refactoring will be considered successful when:

1. All common functionality is extracted to the `common` library
2. Both persona implementations use the common library
3. All tests pass without modification
4. Code duplication is minimized
5. The architecture has clear separation of concerns
6. Documentation is updated to reflect the new architecture
7. A comprehensive test report is generated demonstrating correctness