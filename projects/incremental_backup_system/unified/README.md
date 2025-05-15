# Unified Incremental Backup System Libraries

## Overview
This is a unified implementation of incremental backup system functionality 
that preserves the original package names from multiple persona implementations.

The following packages are available:
- `common` - Shared functionality for all implementations
- `creative_vault` - Specialized backup system for digital artists
- `gamevault` - Specialized backup system for game developers

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