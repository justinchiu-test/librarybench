# Unified File System Analyzer Libraries

## Overview
This is a unified implementation of file system analyzer tools that combines functionality from multiple persona implementations into a shared common library while preserving the original package structures.

The system is designed to support different use cases for file system analysis:
- **Security Auditor** (`file_system_analyzer`): Focused on detecting sensitive information and ensuring regulatory compliance
- **Database Administrator** (`file_system_analyzer_db_admin`): Specialized for database storage management and optimization

## Architecture
The architecture consists of:
- `common`: Shared functionality for all implementations including:
  - Core scanner functionality
  - Pattern matching framework
  - File system utilities
  - Reporting tools
- Persona-specific packages that extend the common functionality:
  - `file_system_analyzer`: Security-focused extensions 
  - `file_system_analyzer_db_admin`: Database-focused extensions

## Key Features
- Unified file system scanning framework
- Flexible pattern matching system
- Customizable reporting
- Multithreaded processing for performance
- Extensible architecture for persona-specific needs

## Installation
Install the library in development mode:

```bash
pip install -e .
```

## Usage
Import the original packages directly or use the common functionality:

```python
# Import from original packages (preserved for backward compatibility)
import file_system_analyzer  # Security auditor persona
import file_system_analyzer_db_admin  # DB admin persona

# Import from common package (for shared functionality)
from common.core import scanner
from common.utils import file_utils
```

## Security Auditor Usage Example
```python
from file_system_analyzer.scanner import ComplianceScanner, ComplianceScanOptions
from file_system_analyzer.detection.patterns import ComplianceCategory, SensitivityLevel

# Configure scan options
options = ComplianceScanOptions(
    scan_options={
        "recursive": True,
        "categories": [ComplianceCategory.PII, ComplianceCategory.PCI],
        "min_sensitivity": SensitivityLevel.MEDIUM,
    },
    output_dir="./results",
    create_baseline=True
)

# Create scanner and scan a directory
scanner = ComplianceScanner(options)
results = scanner.scan_directory("/path/to/scan")
```

## Database Admin Usage Example
```python
from file_system_analyzer_db_admin.interfaces.api import StorageOptimizerAPI
from file_system_analyzer_db_admin.utils.types import DatabaseEngine

# Create API instance
api = StorageOptimizerAPI(output_dir="./output")

# Analyze database files in a directory
result = api.analyze_database_files(
    root_path="/var/lib/mysql",
    recursive=True,
    export_format="json"
)

# Print summary
print(f"Total files: {result.get('total_files_scanned', 0)}")
print(f"MySQL files: {result.get('files_by_engine', {}).get(DatabaseEngine.MYSQL, 0)}")
```

## Testing
Tests are preserved for each persona implementation:

```bash
# Run all tests
pytest

# Run security auditor tests
pytest tests/security_auditor/

# Run database admin tests
pytest tests/db_admin/
```

Record test results with:
```bash
pytest --json-report --json-report-file=report.json --continue-on-collection-errors
```

## Documentation
For more details about the implementation and architecture, see:
- [PLAN.md](./PLAN.md): Architecture and implementation plan
- [INSTRUCTIONS_security_auditor.md](./INSTRUCTIONS_security_auditor.md): Security auditor requirements
- [INSTRUCTIONS_db_admin.md](./INSTRUCTIONS_db_admin.md): Database admin requirements