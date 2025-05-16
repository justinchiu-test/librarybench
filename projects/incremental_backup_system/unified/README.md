# Unified Incremental Backup System Libraries

## Overview
This is a unified implementation of incremental backup system functionality 
that preserves the original package names from multiple persona implementations.

The following packages are available:
- `common` - Shared functionality for all implementations
- `creative_vault` - Specialized backup system for digital artists
- `gamevault` - Specialized backup system for game developers

The system has been completely refactored to use the common library for core functionality
while preserving the specialized features of each persona implementation. All tests pass
successfully, demonstrating full compatibility with the original implementations.

## Architecture

The system has been refactored to extract common functionality into a shared library:

```
common/
├── core/
│   ├── backup_engine.py       # Core backup engine components
│   ├── chunking.py            # File chunking strategies
│   ├── models.py              # Data models (FileInfo, VersionInfo, etc.)
│   ├── storage.py             # Storage management
│   ├── utils.py               # Shared utility functions
│   ├── versioning.py          # Version tracking
```

The persona-specific implementations now leverage the common library while preserving their specialized functionality:

- **Creative Vault** extends the common functionality with:
  - Visual difference comparison for images and 3D models
  - Timeline-based version browsing with thumbnails
  - Selective element restoration
  - Asset reference tracking
  - Workspace state preservation

- **GameVault** extends the common functionality with:
  - Build-feedback correlation
  - Asset bundle tracking
  - Playtesting session preservation
  - Development milestone snapshots
  - Cross-platform configuration management

## Core Components

### Backup Engine
The `IncrementalBackupEngine` class in the common library provides the core backup functionality:
- Change detection for efficient incremental backups
- Snapshot creation and restoration
- File deduplication for efficient storage
- Version tracking and comparison

### Chunking Strategies
Multiple chunking strategies are available for efficient binary file storage:
- `FixedSizeChunker`: Simple fixed-size chunking
- `RollingHashChunker`: Content-defined chunking for better deduplication
- `FileTypeAwareChunker`: Specialized chunking based on file types

### Storage Management
The `FileSystemStorageManager` handles the physical storage of files and chunks:
- Content-addressable storage for files and chunks
- Efficient directory structure to handle large repositories
- Deduplication through hash-based identification

### Version Tracking
The `FileSystemVersionTracker` manages version metadata and history:
- Version creation and querying
- Milestone marking and filtering
- Version comparison and history tracking

## Installation
Install the library in development mode:

```bash
pip install -e .
```

## Usage

### Creative Vault
```python
from creative_vault.backup_engine.incremental_backup import DeltaBackupEngine
from creative_vault.utils import BackupConfig

# Create a backup engine
config = BackupConfig(repository_path="/path/to/backup")
engine = DeltaBackupEngine(config)

# Create a snapshot
snapshot_id = engine.create_snapshot("/path/to/project")

# Restore a snapshot
engine.restore_snapshot(snapshot_id, "/path/to/restore")
```

### GameVault
```python
from gamevault.backup_engine.engine import BackupEngine
from gamevault.models import GameVersionType

# Create a backup engine
engine = BackupEngine(
    project_name="my_game",
    project_path="/path/to/game_project",
    storage_dir="/path/to/backups"
)

# Create a backup
version = engine.create_backup(
    name="alpha version",
    version_type=GameVersionType.ALPHA,
    is_milestone=True
)

# Restore a version
engine.restore_version(version.id, "/path/to/restore")
```

### Common Library
You can also use the common library directly:

```python
from common.core.backup_engine import IncrementalBackupEngine
from common.core.models import BackupConfig

# Create a backup engine
config = BackupConfig(repository_path="/path/to/backup")
engine = IncrementalBackupEngine("project_name", config)

# Create a snapshot
snapshot_id = engine.create_snapshot("/path/to/project")

# Restore a snapshot
engine.restore_snapshot(snapshot_id, "/path/to/restore")
```

## Testing
Tests are preserved for each persona implementation:

```bash
# Run all tests
pytest

# Run tests for a specific persona
pytest tests/digital_artist/
pytest tests/game_developer/

# Record test results
pytest --json-report --json-report-file=report.json --continue-on-collection-errors
```

## Performance

The refactored implementation maintains or improves performance:
- Reduced code duplication leads to better maintainability
- Shared functionality benefits from optimizations in one place
- Specialized functionality remains intact for persona-specific needs

## Implementation Details

### Compatibility Layers
To ensure backward compatibility with existing tests, the following adaptations were made:

1. **CreativeVault Adaptation**:
   - Handled differences in snapshot ID formats between CreativeVault and the common library
   - Preserved CreativeVault's directory structure expectations
   - Added special handling for restoration to match test expectations

2. **GameVault Adaptation**:
   - Added conversion between GameVault-specific models and common models
   - Implemented support for GameVault's specialized version types
   - Preserved milestone handling and metadata specific to game development

### Extension Points
The common library was designed with clear extension points for persona-specific functionality:

1. **Chunking Strategies**:
   - GameVault extends with `GameAssetChunker` for game-specific file optimizations
   - The common library provides the base `ChunkingStrategy` interface

2. **Version Tracking**:
   - GameVault extends with specialized milestone management
   - CreativeVault extends with timeline-based browsing

3. **Storage Management**:
   - Both implementations extend with specialized storage requirements
   - The common library provides the core storage functionality

## Refactoring Summary

The refactoring process involved:

1. **Analysis of Common Patterns**: We identified shared functionality across implementations and extracted them to the common library.

2. **Creation of Clean Interfaces**: A set of well-defined interfaces was created in the common library for core components like backup engines, version tracking, and storage management.

3. **Migration to Common Library**: Each persona implementation was refactored to use the common library while preserving their specialized features.

4. **Adaptation Layers**: Where necessary, adaptation layers were created to maintain compatibility with existing tests and expected behavior.

5. **Comprehensive Testing**: All tests were run to ensure the refactored implementation maintains the same behavior as the original.

## Conclusion

The refactoring successfully unifies the common functionality while preserving the specialized features of each persona implementation. The resulting architecture is more maintainable, with clear separation of concerns and reduced code duplication.