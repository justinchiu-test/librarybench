# Common Core Module

This module provides the fundamental building blocks for text editor implementations across both the student and writer text editors. It includes abstractions for text content management, positioning, history tracking, and file operations.

## Position Implementation

The position module (`position.py`) provides a unified way to handle cursor positioning across different types of text editors:

### Position Classes

1. **Position (Abstract Base Class)**:
   - Defines the common interface for all position implementations
   - Provides methods for comparing positions and calculating offsets

2. **LineColumnPosition**:
   - Represents a traditional cursor position with line and column coordinates
   - Compatible with the student text editor's buffer-based approach
   - Provides navigation methods (move up/down/left/right, jump to line start/end, etc.)

3. **StructuredPosition**:
   - Represents a position in a structured document with sections and segments
   - Compatible with the writer text editor's document-based approach
   - Provides structured navigation (move between sections/segments, jump to segment start/end, etc.)

### Content Protocols

The module defines protocols that content objects must implement to work with the position classes:

1. **TextContentProtocol**: Base protocol for all text content
2. **LineBasedContentProtocol**: For line-based text content (like `TextBuffer`)
3. **StructuredContentProtocol**: For hierarchical content (like `Document`)

### Factory Function

The `create_position()` function examines a content object and creates the appropriate position class for it automatically.

## Usage Examples

### For Student Text Editor

```python
from common.core.position import create_position

# Create a position for a line-based buffer
position = create_position(text_buffer)

# Navigate using the position
position.move_to(5, 10)  # Move to line 5, column 10
position.move_down(2)    # Move down 2 lines
position.move_to_line_end()  # Move to end of line
```

### For Writer Text Editor

```python
from common.core.position import create_position

# Create a position for a structured document
position = create_position(document)

# Navigate using the position
position.set_position(1, 2, 5)  # Move to section 1, segment 2, offset 5
position.move_to_next_segment()  # Move to next segment
position.move_to_section_start()  # Move to start of section
```

## Integration

This common position implementation allows for creating tools and features that can work with both types of text editors by relying on the common interface defined by the `Position` base class.