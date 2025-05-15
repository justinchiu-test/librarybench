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
  - `LineColumnPosition`: Simple line/column coordinate system (used by text_editor)
  - `StructuredPosition`: Hierarchical position system for structured documents (used by writer_text_editor)

- **Text Content Module**: Text storage and manipulation
  - `TextContent`: Base abstract class for text content
  - `LineBasedTextContent`: Simple line-based text storage (used by text_editor)
  - `StructuredTextContent`: Complex document model with hierarchical organization (used by writer_text_editor)
  - `TextSegment`, `Section`, `Revision`: Building blocks for structured content

- **History Module**: Undo/redo functionality
  - `Operation`: Base class for edit operations
  - `InsertOperation`, `DeleteOperation`, `ReplaceOperation`: Concrete operations
  - `History`: Tracks operation history for undo/redo

- **File Manager Module**: File I/O operations
  - Loading and saving content
  - Tracking file modifications
  - File metadata management
  - Support for structured content serialization

- **Event System**: Event handling for loose coupling between components
  - `EventSystem`: Central event manager
  - `EventType`: Enumeration of supported event types
  - `EventData`: Base class for event data

- **Configuration Manager**: Settings management
  - `ConfigManager`: Configuration settings manager
  - `ConfigValue`: Typed configuration values with validation

- **Text Operations**: Utility functions for text analysis and manipulation
  - Word counting and readability metrics
  - Text formatting and transformation
  - Content analysis utilities

### Implementation-Specific Extensions

Each persona-specific implementation extends the common components with specialized functionality:

#### Text Editor (Student Persona)
- `Buffer`: Extends LineBasedTextContent for simple text storage
- `Cursor`: Uses LineColumnPosition for navigation
- `Editor`: Combines buffer, cursor, and history
- Additional modules for learning, customization, and coding exercises

#### Writer Text Editor (Writer Persona)
- `Document`: Extends StructuredTextContent for document management
- Navigation system for non-linear document traversal
- Focus mode for distraction-free writing
- Statistics for tracking writing metrics
- Revision system for document versions

## Implementation Details

### Inheritance Structure
Components in the common library use abstract base classes and protocols to define clear interfaces. Persona-specific implementations extend these base classes, adding specialized functionality while preserving the common interfaces.

### Extension Points
The architecture provides several extension points:
- Custom position types extending the Position base class
- Custom content storage models extending the TextContent base class
- Event system for custom event types and handlers
- Configuration system for persona-specific settings

### Backward Compatibility
The refactored implementation maintains backward compatibility with all original tests. Wrapper classes and compatibility methods ensure existing code continues to work without modification.

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
from common.core import position, text_content
```

Example using the common library directly:

```python
from common.core.text_content import LineBasedTextContent
from common.core.position import LineColumnPosition

# Create a text content instance
content = LineBasedTextContent("Hello\nWorld")

# Create a position
position = LineColumnPosition(line=0, column=0)

# Manipulate content
content.insert(position, "Greeting: ")
print(content.get_text())  # "Greeting: Hello\nWorld"
```

## Testing
Tests are preserved for each persona implementation:

```bash
# Run all tests
pytest

# Run tests for a specific persona
pytest tests/student/
pytest tests/writer/

# Run a specific test file
pytest tests/student/test_core.py
```

Record test results with:
```bash
pytest --json-report --json-report-file=report.json --continue-on-collection-errors
```