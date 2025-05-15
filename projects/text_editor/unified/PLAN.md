# Architecture and Design Plan for Unified Text Editor Library (COMPLETED)

This document outlines the architecture plan for creating a unified common library that can be used by both the student and writer text editor implementations. This plan has been successfully implemented and all tests are now passing.

## 1. Analysis Summary

### Common Patterns

Based on an analysis of both the `text_editor` (student) and `writer_text_editor` (writer) implementations, several common patterns and functionality have been identified:

1. **Text Storage and Manipulation**
   - Both implementations need to store and manipulate text
   - Both need operations for inserting, deleting, and replacing text
   - Both track content across multiple edits

2. **Navigation and Positioning**
   - Both need to track positions within text content
   - Both need to navigate through content based on different criteria

3. **History and Revision Management**
   - Both track changes to text
   - Both need undo/redo capabilities
   - Writer implementation has more sophisticated revision management

4. **File Operations**
   - Both need to load from and save to files
   - Both handle file path management and modification tracking

### Key Differences

The implementations differ significantly in their focus:

1. **Student Implementation**
   - Progressive feature complexity for learning
   - Implementation-focused learning mode
   - Customization playground
   - Interview preparation focus
   - Study session capabilities

2. **Writer Implementation**
   - Focus mode for distraction-free writing
   - Writing statistics and analytics
   - Narrative and character tracking
   - Non-linear document navigation
   - Sophisticated revision management

## 2. Common Library Architecture

### Core Components

The common library will be structured as follows:

#### `common.core`

1. **TextContent**
   - Abstract base class for text storage
   - Implementations for different storage strategies:
     - `LineBasedTextContent` (used by student editor)
     - `StructuredTextContent` (used by writer editor)
   - Common interface for text manipulation:
     - `insert`, `delete`, `replace` operations
     - Content retrieval methods
     - Word counting and statistics

2. **Position**
   - Abstract base class for tracking positions in text
   - Implementations:
     - `LineColumnPosition` (used by student editor)
     - `StructuredPosition` (used by writer editor)
   - Common operations:
     - Position comparison
     - Boundary validation
     - Movement operations

3. **History**
   - Abstract base class for change tracking
   - Base operation classes: `InsertOperation`, `DeleteOperation`, `ReplaceOperation`
   - Core undo/redo functionality
   - Extension points for more complex revision tracking

4. **FileManager**
   - Unified file I/O operations
   - Path management
   - Modification tracking
   - Loading and saving content

#### Common Utilities

1. **EventSystem**
   - Event definition and subscription
   - Document change notifications
   - Content update events

2. **TextOperations**
   - Text parsing and analysis
   - Word and sentence identification
   - Common text transformation operations

3. **ConfigurationManager**
   - Settings management
   - Feature configuration
   - User preferences

## 3. Extension Points

The common library will provide clear extension points for persona-specific functionality:

1. **TextContent Extensions**
   - Custom text storage implementations
   - Specialized content operations
   - Content type validation

2. **Position Extensions**
   - Custom positioning systems
   - Navigation strategies
   - View-specific positioning

3. **History Extensions**
   - Enhanced revision tracking
   - Diff generation
   - Multi-version management

4. **View Management Extensions**
   - Different presentation strategies
   - Specialized navigation
   - Content filtering

## 4. Migration Strategy

### Student Editor Migration

1. **Core Module**
   - Replace `TextBuffer` with common `LineBasedTextContent`
   - Replace `Cursor` with common `LineColumnPosition`
   - Replace `History` with common `History`
   - Replace `FileManager` with common `FileManager`
   - Adapt `Editor` to use common components

2. **Specialized Modules**
   - Keep specialized functionality (customization, features, etc.)
   - Update to use common base classes
   - Implement required extension points

### Writer Editor Migration

1. **Document Module**
   - Replace document structure with `StructuredTextContent`
   - Adapt `TextSegment`, `Section`, etc. to use common base classes
   - Use common interfaces for content manipulation

2. **Navigation and Focus**
   - Implement specialized position types with common base
   - Extend common navigation capabilities
   - Keep focus-specific functionality

3. **Revision System**
   - Extend common `History` with more sophisticated tracking
   - Implement diff generation using common interfaces
   - Retain version naming and management capabilities

4. **Specialized Features**
   - Keep narrative tracking and statistics modules
   - Update to use common interfaces
   - Implement required extension points

## 5. Interface Definitions

### TextContent Interface

```python
class TextContent(ABC):
    @abstractmethod
    def insert(self, position: Position, text: str) -> None:
        """Insert text at the specified position."""
        pass
        
    @abstractmethod
    def delete(self, start: Position, end: Position) -> None:
        """Delete text between start and end positions."""
        pass
        
    @abstractmethod
    def replace(self, start: Position, end: Position, text: str) -> None:
        """Replace text between start and end positions with new text."""
        pass
        
    @abstractmethod
    def get_text(self, start: Optional[Position] = None, end: Optional[Position] = None) -> str:
        """Get text between start and end positions."""
        pass
        
    @abstractmethod
    def get_line_count(self) -> int:
        """Get the number of lines in the content."""
        pass
```

### Position Interface

```python
class Position(ABC):
    @abstractmethod
    def move_up(self, count: int = 1) -> None:
        """Move position up by count units."""
        pass
        
    @abstractmethod
    def move_down(self, count: int = 1) -> None:
        """Move position down by count units."""
        pass
        
    @abstractmethod
    def move_left(self, count: int = 1) -> None:
        """Move position left by count units."""
        pass
        
    @abstractmethod
    def move_right(self, count: int = 1) -> None:
        """Move position right by count units."""
        pass
        
    @abstractmethod
    def is_valid(self, content: TextContent) -> bool:
        """Check if position is valid for the given content."""
        pass
```

### History Interface

```python
class Operation(ABC):
    @abstractmethod
    def apply(self, content: TextContent) -> None:
        """Apply operation to content."""
        pass
        
    @abstractmethod
    def undo(self, content: TextContent) -> None:
        """Undo operation on content."""
        pass

class History(ABC):
    @abstractmethod
    def record_operation(self, operation: Operation) -> None:
        """Record a new operation in history."""
        pass
        
    @abstractmethod
    def undo(self, content: TextContent) -> bool:
        """Undo last operation and return success."""
        pass
        
    @abstractmethod
    def redo(self, content: TextContent) -> bool:
        """Redo previously undone operation and return success."""
        pass
```

## 6. Implementation Plan

### Phase 1: Core Components

1. Implement base TextContent and concrete implementations
2. Implement base Position and concrete implementations
3. Implement base History and operation classes
4. Implement FileManager and utilities

### Phase 2: Student Editor Migration

1. Update text_editor core modules to use common library
2. Update specialized modules to use common interfaces
3. Test with student-specific test suite

### Phase 3: Writer Editor Migration

1. Update writer_text_editor document model to use common library
2. Update specialized features to use common interfaces
3. Test with writer-specific test suite

### Phase 4: Integration Testing

1. Run all tests for both personas
2. Fine-tune implementations based on test results
3. Optimize common library for performance

## 7. Risks and Mitigations

### Risks

1. **Interface Generality**: Creating interfaces general enough for both personas but specific enough to be useful
   - Mitigation: Start with minimal interfaces and extend based on concrete usage

2. **Performance Overhead**: Adding abstraction could impact performance
   - Mitigation: Performance testing, optimizing critical paths

3. **Regression**: Changes might break existing functionality
   - Mitigation: Comprehensive test coverage, incremental refactoring

4. **Interface Complexity**: Overly complex interfaces might be hard to use
   - Mitigation: Regular review of interface design, favoring simplicity

## 8. Success Metrics

1. **Code Reduction**: Measure percentage of shared code
2. **Test Pass Rate**: All tests for both personas must pass
3. **Performance**: Verify performance meets or exceeds original implementations
4. **Maintainability**: Improved code structure and reduced duplication

## 9. Directory Structure

```
unified/
├── common/                                # Common functionality across all implementations
│   ├── __init__.py
│   ├── README.md
│   └── core/                              # Core data structures and algorithms
│       ├── __init__.py
│       ├── text_content.py                # Abstract and concrete TextContent implementations
│       ├── position.py                    # Abstract and concrete Position implementations
│       ├── history.py                     # History and Operation classes
│       ├── file_manager.py                # File operations management
│       ├── event_system.py                # Event system for document changes
│       ├── text_operations.py             # Text analysis and manipulation utilities
│       └── config_manager.py              # Configuration management
├── text_editor/                           # Student persona implementation
│   ├── __init__.py
│   ├── README.md
│   ├── core/                              # Core modules (refactored to use common library)
│   ├── customization/                     # Student-specific customization features
│   ├── features/                          # Student-specific feature management
│   ├── interview/                         # Interview preparation functionality
│   ├── learning/                          # Learning mode functionality
│   └── study/                             # Study session tracking
├── writer_text_editor/                    # Writer persona implementation
│   ├── __init__.py
│   ├── README.md
│   ├── client.py                          # Main client (refactored to use common library)
│   ├── document.py                        # Document model (refactored to use common library)
│   ├── focus.py                           # Focus mode implementation
│   ├── narrative.py                       # Character and plot tracking
│   ├── navigation.py                      # Non-linear navigation
│   ├── revision.py                        # Revision management (refactored to use common library)
│   ├── statistics.py                      # Writing statistics
│   └── utils/                             # Utility functions
├── tests/                                 # Tests directory
│   ├── student/                           # Tests for student implementation
│   └── writer/                            # Tests for writer implementation
├── INSTRUCTIONS_student.md                # Original instructions for student persona
├── INSTRUCTIONS_writer.md                 # Original instructions for writer persona
├── PLAN.md                                # This document
├── README.md                              # Project documentation
├── conftest.py                            # Pytest configuration
├── pyproject.toml                         # Project configuration
└── setup.py                               # Installation script
```

## 10. Integration Strategy

- Original package names are preserved, so existing tests work without modification
- Common functionality is moved to the common package
- Persona implementations are refactored to use the common package
- All tests must pass without modification
- Persona-specific extensions continue to live in their original packages