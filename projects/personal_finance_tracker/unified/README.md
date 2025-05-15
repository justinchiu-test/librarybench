# Unified Personal Finance Tracker Libraries

## Overview
This is a unified implementation of personal finance tracker functionality 
that preserves the original package names from multiple persona implementations.

The following packages are available:
- `common` - Shared functionality for all implementations
- `ethical_finance` - `personal_finance_tracker`

## Installation
Install the library in development mode:

```bash
pip install -e .
```

## Usage
Import the original packages directly:

```python
# Import from original packages (preserved for backward compatibility)
import personal_finance_tracker # Example using first package

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
