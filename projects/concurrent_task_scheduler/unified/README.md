# Unified Concurrent Task Scheduler Libraries

## Overview
This is a unified implementation of concurrent task scheduler functionality 
that preserves the original package names from multiple persona implementations.

The following packages are available:
- `common` - Shared functionality for all implementations
- `concurrent_task_scheduler` - `render_farm_manager`

## Installation
Install the library in development mode:

```bash
pip install -e .
```

## Usage
Import the original packages directly:

```python
# Import from original packages (preserved for backward compatibility)
import render_farm_manager # Example using first package

# Import from common package (for shared functionality)
from common import core
```

## Testing
Tests are preserved for each persona implementation:

```bash
cd tests
pytest
```

Record test results with:
```bash
pytest --json-report --json-report-file=report.json --continue-on-collection-errors
```
