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
  - `QueryResult`: Standardized result representation with domain-specific extensions
  - `LegalQueryResult`: Specialized query result for legal discovery with document management

- **Pattern Detection**:
  - `BasePatternDetector`: Framework for all pattern-based detection
  - `PatternMatcher`: Pattern matching with confidence scoring
  - `PatternMatch`: Match result representation with metadata
  - `PIIPatternMatch`: Specialized match for PII detection with sensitivity levels
  - `SQLPatternDetector`: Detector for SQL query patterns with privacy concerns

- **Common Models**:
  - Shared enumerations for query types, privacy functions, etc.
  - Base data models for consistent representation
  - Legal-specific models for document types, privilege status, and timeframes
  - Document class with common content access patterns

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

## Refactored Components
The refactoring process has identified and unified several key components common to both persona implementations:

1. **Document Handling**:
   - Unified `Document` base class with consistent content property access
   - Specialized document types (e.g., `EmailDocument`) that inherit from the common base

2. **Pattern Detection**:
   - Common pattern detection framework with specialized implementations
   - PII pattern detection with sensitivity levels and categories
   - SQL query pattern detection for privacy and security analysis

3. **Query Processing**:
   - Standardized query execution context
   - Common query result framework with domain-specific extensions
   - Shared query clause representation for legal and privacy domains

4. **Legal-specific Extensions**:
   - Legal document timeframe handling
   - Privilege detection and status tracking
   - Document relevance scoring

5. **Privacy-specific Extensions**:
   - Data anonymization methods
   - PII detection and sensitivity analysis
   - Policy enforcement and validation

## Refactoring Implementation Status

The refactoring has been completed with the following status:

- ✅ Core interfaces have been defined in the common library
- ✅ Pattern detection framework has been implemented
- ✅ PIIPatternDetector has been refactored to use the common pattern detection framework
- ✅ PII detection in the privacy interpreter is fully compatible with the common framework
- ✅ Legal discovery interpreter components have been refactored
- ✅ PrivilegeDetector has been migrated to use the common pattern detection framework
- ✅ Legal models have been shared in the common library
- ✅ All tests are now passing

### Completed Components

1. **Common Pattern Detection**: Enhanced the pattern detection framework with specialized handlers for PII and legal patterns.
   
2. **Refactoring Privacy Interpreter**: Migrated the PIIDetector to use the common pattern detection framework. Fixed compatibility issues with the common PIIPatternMatch class.

3. **Refactoring Legal Discovery Interpreter**: Successfully migrated the PrivilegeDetector to use the common pattern detection framework. Moved shared legal models to the common library.

### Key Improvements

1. **PII Detection Compatibility**: Fixed compatibility issues between the common PIIPatternMatch and the privacy-specific PIIMatch classes through proper metadata handling.

2. **Legal Pattern Detection**: Implemented a common detection framework for legal patterns that can be used for privilege detection and other legal discovery tasks.

3. **Shared Models**: Moved shared models for privilege detection, PII categories, and other common data structures to the common library to reduce code duplication.

4. **Backward Compatibility**: Maintained backward compatibility with existing tests while still taking advantage of the common components.

## Testing
Tests are preserved for each persona implementation:

```bash
# Run tests for data privacy officer
pytest tests/data_privacy_officer/

# Run tests for legal discovery specialist
pytest tests/legal_discovery_specialist/

# Run all tests
pytest
```

Record test results with:
```bash
pytest --json-report --json-report-file=report.json --continue-on-collection-errors
```

All tests are now passing in the refactored implementation, ensuring backward compatibility while providing enhanced functionality through the common components.
