# Unified Text Editor Libraries

## Overview
This is a unified implementation of text editor functionality that preserves the original package names from multiple persona implementations. The project refactors common patterns and functionality into a shared library while maintaining backward compatibility with the original implementations.

The following packages are available:
- `common` - Shared core functionality and abstractions for all implementations
- `text_editor` - Student-focused implementation with learning and customization features
- `writer_text_editor` - Writer-focused implementation with document management and creative writing features

## Architecture

### Common Library
The common package provides shared abstractions and implementations for core text editor functionality:

- **Position Module**: Abstract and concrete position classes
  - `Position`: Base abstract class for positions within text content
  - `LineColumnPosition`: Simple line/column coordinate system
  - `StructuredPosition`: Hierarchical position system for structured documents

- **Text Content Module**: Text storage and manipulation
  - `TextContent`: Base abstract class for text content
  - `LineBasedTextContent`: Simple line-based text storage
  - `StructuredTextContent`: Complex document model with hierarchical organization

- **History Module**: Undo/redo functionality
  - `Operation`: Base class for edit operations
  - `InsertOperation`, `DeleteOperation`, `ReplaceOperation`: Concrete operations
  - `History`: Tracks operation history for undo/redo

- **File Manager Module**: File I/O operations
  - Loading and saving content
  - Tracking file modifications
  - File metadata management

- **Event System**: Event handling for loose coupling between components

Each persona-specific implementation extends these common components while preserving their unique features and interfaces.

## Installation
Install the library in development mode:

```bash
pip install -e .
```

## Usage
Import the original packages directly:

```python
# Import from original packages (preserved for backward compatibility)
import text_editor # Example using first package

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
