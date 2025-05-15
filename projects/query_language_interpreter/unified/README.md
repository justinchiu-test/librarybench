# Unified Query Language Interpreter Libraries

## Overview
This is a unified implementation of query language interpreter functionality 
that preserves the original package names from multiple persona implementations.

The following packages are available:
- `common` - Shared functionality for all implementations
- `legal_discovery_interpreter` - Interpreter for legal discovery specialist persona
- `privacy_query_interpreter` - Interpreter for data privacy officer persona

## Architecture
The library has been refactored to use a common set of core components while preserving domain-specific functionality for each persona. The common library provides:

- **Core Components**:
  - `BaseQuery`: Core query representation with execution context
  - `BaseInterpreter`: Common interpreter interface with parse/execute methods
  - `QueryResult`: Standardized result representation

- **Pattern Detection**:
  - `BasePatternDetector`: Framework for all pattern-based detection
  - `PatternMatcher`: Pattern matching with confidence scoring
  - `PatternMatch`: Match result representation with metadata

- **Common Models**:
  - Shared enumerations for query types, privacy functions, etc.
  - Base data models for consistent representation

## Installation
Install the library in development mode:

```bash
pip install -e .
```

## Usage
Import the original packages directly:

```python
# Import from original packages (preserved for backward compatibility)
from privacy_query_interpreter.query_engine.engine import PrivacyQueryEngine
from legal_discovery_interpreter.core.interpreter import LegalDiscoveryInterpreter

# Import from common package (for shared functionality)
from common.core.interpreter import BaseInterpreter
from common.pattern.detector import BasePatternDetector
```

### Example: Pattern Detection

```python
from common.pattern.detector import BasePatternDetector
from common.models.enums import PrivacyFunction

# Create a pattern detector for privacy functions
class PrivacyPatternDetector(BasePatternDetector):
    def __init__(self):
        super().__init__()
        # Initialize patterns for privacy functions
        for func in PrivacyFunction:
            self.add_pattern(
                pattern_id=f"privacy_{func.value.lower()}",
                regex=rf'{func.value}\s*\(([^)]+)\)',
                category="privacy_function",
                metadata={"function_type": func.value}
            )
```

## Testing
Tests are preserved for each persona implementation:

```bash
# Run tests for data privacy officer
pytest tests/data_privacy_officer/

# Run tests for legal discovery specialist
pytest tests/legal_discovery_specialist/
```

Record test results with:
```bash
pytest --json-report --json-report-file=report.json --continue-on-collection-errors
```
