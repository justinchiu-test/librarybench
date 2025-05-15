# Common Library for Text Editors

This package contains common functionality that is shared between the student and writer text editor implementations.

## Core Components

- `TextContent`: Abstract base class for text storage with concrete implementations
- `Position`: Abstract base class for tracking positions in text with concrete implementations
- `History`: Base classes for tracking changes and supporting undo/redo operations
- `FileManager`: Common file I/O operations
- Utility functions for text operations, event handling, and configuration

## Structure

- `core/`: Core data structures and algorithms
  - `text_content.py`: Abstract and concrete TextContent implementations
  - `position.py`: Abstract and concrete Position implementations
  - `history.py`: History and Operation classes
  - `file_manager.py`: File operations management
  - `event_system.py`: Event system for document changes
  - `text_operations.py`: Text analysis and manipulation utilities
  - `config_manager.py`: Configuration management

## Usage

Import the common components in your code:

```python
from common.core import TextContent, Position, History, FileManager
from common.core.text_content import LineBasedTextContent, StructuredTextContent
from common.core.position import LineColumnPosition, StructuredPosition
```

See individual module documentation for specific usage examples.