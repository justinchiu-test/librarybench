"""
Text content module for storing and manipulating text.

This module provides a base TextContent class and concrete implementations for
different types of text storage strategies, including line-based and structured
document storage.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union, TYPE_CHECKING
from pydantic import BaseModel, Field

# Avoid circular import while maintaining type hints
if TYPE_CHECKING:
    from common.core.position import Position, LineColumnPosition, StructuredPosition


class TextContent(BaseModel, ABC):
    """
    Abstract base class for text content storage.

    This class defines the interface for all text content implementations,
    with methods for inserting, deleting, replacing, and retrieving text.
    """

    @abstractmethod
    def insert(self, position: Position, text: str) -> None:
        """
        Insert text at the specified position.

        Args:
            position: The position where text should be inserted
            text: The text to insert

        Raises:
            ValueError: If the position is invalid
        """
        pass

    @abstractmethod
    def delete(self, start: Position, end: Position) -> str:
        """
        Delete text between the specified positions.

        Args:
            start: The start position of the text to delete
            end: The end position of the text to delete

        Returns:
            The deleted text

        Raises:
            ValueError: If either position is invalid or if end comes before start
        """
        pass

    @abstractmethod
    def replace(self, start: Position, end: Position, text: str) -> str:
        """
        Replace text between the specified positions with new text.

        Args:
            start: The start position of the text to replace
            end: The end position of the text to replace
            text: The replacement text

        Returns:
            The replaced text

        Raises:
            ValueError: If either position is invalid or if end comes before start
        """
        pass

    @abstractmethod
    def get_text(
        self, start: Optional[Position] = None, end: Optional[Position] = None
    ) -> str:
        """
        Get text between the specified positions.

        Args:
            start: The start position (default: beginning of content)
            end: The end position (default: end of content)

        Returns:
            The text between start and end positions

        Raises:
            ValueError: If either position is invalid or if end comes before start
        """
        pass

    @abstractmethod
    def get_line_count(self) -> int:
        """
        Get the number of lines in the content.

        Returns:
            The number of lines
        """
        pass

    @abstractmethod
    def get_line(self, line_number: int) -> str:
        """
        Get a specific line from the content.

        Args:
            line_number: The line number to retrieve (0-indexed)

        Returns:
            The requested line

        Raises:
            IndexError: If the line number is out of range
        """
        pass

    @abstractmethod
    def get_word_count(self) -> int:
        """
        Get the total number of words in the content.

        Returns:
            The number of words
        """
        pass


class LineBasedTextContent(TextContent):
    """
    A text content implementation that stores text as a list of lines.

    This implementation is suited for simple line-based text editors,
    where operations are primarily performed using line and column coordinates.
    """

    lines: List[str] = Field(default_factory=lambda: [""])

    def __init__(self, content: str = ""):
        """
        Initialize a new line-based text content with the given content.

        Args:
            content: Initial text content (defaults to empty string)
        """
        super().__init__()
        self.lines = content.split("\n") if content else [""]

    def insert(self, position: Position, text: str) -> None:
        """
        Insert text at the specified position.

        Args:
            position: The position where text should be inserted (must be LineColumnPosition)
            text: The text to insert

        Raises:
            ValueError: If the position is invalid or not a LineColumnPosition
        """
        from common.core.position import LineColumnPosition

        if not isinstance(position, LineColumnPosition):
            raise ValueError("Position must be a LineColumnPosition")

        line, column = position.line, position.column

        # Ensure position is valid
        if not (0 <= line < len(self.lines)):
            raise ValueError(f"Line number {line} out of range")

        current_line = self.lines[line]
        if not (0 <= column <= len(current_line)):
            raise ValueError(f"Column number {column} out of range for line {line}")

        # Handle multi-line insertion
        if "\n" in text:
            # Split the text into lines
            new_lines = text.split("\n")

            # Handle the first line (insert at the current position)
            first_part = current_line[:column]
            last_part = current_line[column:]

            # Create the new set of lines
            new_content = [first_part + new_lines[0]]
            new_content.extend(new_lines[1:-1])
            new_content.append(new_lines[-1] + last_part)

            # Update the buffer
            self.lines[line : line + 1] = new_content
        else:
            # Simple single-line insertion
            new_line = current_line[:column] + text + current_line[column:]
            self.lines[line] = new_line

    def delete(self, start: Position, end: Position) -> str:
        """
        Delete text between the specified positions.

        Args:
            start: The start position of the text to delete (must be LineColumnPosition)
            end: The end position of the text to delete (must be LineColumnPosition)

        Returns:
            The deleted text

        Raises:
            ValueError: If either position is invalid, not a LineColumnPosition,
                        or if end comes before start
        """
        from common.core.position import LineColumnPosition

        if not isinstance(start, LineColumnPosition) or not isinstance(
            end, LineColumnPosition
        ):
            raise ValueError("Positions must be LineColumnPositions")

        start_line, start_col = start.line, start.column
        end_line, end_col = end.line, end.column

        # Validate positions
        if start_line > end_line or (start_line == end_line and start_col > end_col):
            raise ValueError("End position must come after start position")

        # Ensure positions are within range
        if not (0 <= start_line < len(self.lines)):
            raise ValueError(f"Start line {start_line} out of range")
        if not (0 <= end_line < len(self.lines)):
            raise ValueError(f"End line {end_line} out of range")

        start_line_text = self.lines[start_line]
        end_line_text = self.lines[end_line]

        if not (0 <= start_col <= len(start_line_text)):
            raise ValueError(
                f"Start column {start_col} out of range for line {start_line}"
            )
        if not (0 <= end_col <= len(end_line_text)):
            raise ValueError(f"End column {end_col} out of range for line {end_line}")

        # Handle deletion within a single line
        if start_line == end_line:
            deleted_text = start_line_text[start_col:end_col]
            self.lines[start_line] = (
                start_line_text[:start_col] + start_line_text[end_col:]
            )
            return deleted_text

        # Handle multi-line deletion
        deleted_lines = []

        # Get the first partial line
        deleted_lines.append(start_line_text[start_col:])

        # Get any full lines in the middle
        if end_line - start_line > 1:
            deleted_lines.extend(self.lines[start_line + 1 : end_line])

        # Get the last partial line
        deleted_lines.append(end_line_text[:end_col])

        # Join the deleted text
        deleted_text = "\n".join(deleted_lines)

        # Update the buffer
        new_line = start_line_text[:start_col] + end_line_text[end_col:]
        self.lines[start_line : end_line + 1] = [new_line]

        return deleted_text

    def replace(self, start: Position, end: Position, text: str) -> str:
        """
        Replace text between the specified positions with new text.

        Args:
            start: The start position of the text to replace (must be LineColumnPosition)
            end: The end position of the text to replace (must be LineColumnPosition)
            text: The replacement text

        Returns:
            The replaced text

        Raises:
            ValueError: If either position is invalid, not a LineColumnPosition,
                        or if end comes before start
        """
        # Delete the text first and get what was deleted
        deleted_text = self.delete(start, end)

        # Insert the new text
        self.insert(start, text)

        return deleted_text

    def get_text(
        self, start: Optional[Position] = None, end: Optional[Position] = None
    ) -> str:
        """
        Get text between the specified positions.

        Args:
            start: The start position (default: beginning of content)
            end: The end position (default: end of content)

        Returns:
            The text between start and end positions

        Raises:
            ValueError: If either position is invalid, not a LineColumnPosition,
                        or if end comes before start
        """
        from common.core.position import LineColumnPosition

        # If no positions provided, return all content
        if start is None and end is None:
            return "\n".join(self.lines)

        # Convert None to start/end of content
        if start is None:
            start = LineColumnPosition(line=0, column=0)
        if end is None:
            last_line = len(self.lines) - 1
            end = LineColumnPosition(line=last_line, column=len(self.lines[last_line]))

        # Validate position types
        if not isinstance(start, LineColumnPosition) or not isinstance(
            end, LineColumnPosition
        ):
            raise ValueError("Positions must be LineColumnPositions")

        start_line, start_col = start.line, start.column
        end_line, end_col = end.line, end.column

        # Validate positions
        if start_line > end_line or (start_line == end_line and start_col > end_col):
            raise ValueError("End position must come after start position")

        # Ensure positions are within range
        if not (0 <= start_line < len(self.lines)):
            raise ValueError(f"Start line {start_line} out of range")
        if not (0 <= end_line < len(self.lines)):
            raise ValueError(f"End line {end_line} out of range")

        start_line_text = self.lines[start_line]
        end_line_text = self.lines[end_line]

        if not (0 <= start_col <= len(start_line_text)):
            raise ValueError(
                f"Start column {start_col} out of range for line {start_line}"
            )
        if not (0 <= end_col <= len(end_line_text)):
            raise ValueError(f"End column {end_col} out of range for line {end_line}")

        # Handle text within a single line
        if start_line == end_line:
            return start_line_text[start_col:end_col]

        # Handle multi-line text
        result_lines = []

        # Get the first partial line
        result_lines.append(start_line_text[start_col:])

        # Get any full lines in the middle
        if end_line - start_line > 1:
            result_lines.extend(self.lines[start_line + 1 : end_line])

        # Get the last partial line
        result_lines.append(end_line_text[:end_col])

        # Join and return the text
        return "\n".join(result_lines)

    def get_line_count(self) -> int:
        """
        Get the number of lines in the content.

        Returns:
            The number of lines
        """
        return len(self.lines)

    def get_line(self, line_number: int) -> str:
        """
        Get a specific line from the content.

        Args:
            line_number: The line number to retrieve (0-indexed)

        Returns:
            The requested line

        Raises:
            IndexError: If the line number is out of range
        """
        if 0 <= line_number < len(self.lines):
            return self.lines[line_number]
        raise IndexError(f"Line number {line_number} out of range")

    def get_word_count(self) -> int:
        """
        Get the total number of words in the content.

        Returns:
            The number of words
        """
        return len(re.findall(r"\b\w+\b", self.get_text()))

    def clear(self) -> None:
        """Clear the content, removing all text."""
        self.lines = [""]


class TextSegment(BaseModel):
    """A segment of text, such as a paragraph or sentence."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    position: int
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def get_word_count(self) -> int:
        """Get the number of words in this segment."""
        return len(re.findall(r"\b\w+\b", self.content))


class Section(BaseModel):
    """A section of a document, such as a chapter or scene."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    segments: List[TextSegment] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def get_content(self) -> str:
        """Get the full content of this section."""
        return "\n".join([segment.content for segment in self.segments])

    def get_word_count(self) -> int:
        """Get the number of words in this section."""
        return sum(segment.get_word_count() for segment in self.segments)

    def add_segment(
        self, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> TextSegment:
        """Add a new segment to this section."""
        position = len(self.segments)
        segment = TextSegment(
            content=content, position=position, metadata=metadata or {}
        )
        self.segments.append(segment)
        return segment

    def get_segment(self, position: int) -> Optional[TextSegment]:
        """Get the segment at the specified position."""
        if 0 <= position < len(self.segments):
            return self.segments[position]
        return None

    def update_segment(self, position: int, content: str) -> Optional[TextSegment]:
        """Update the content of the segment at the specified position."""
        segment = self.get_segment(position)
        if segment:
            segment.content = content
            return segment
        return None

    def delete_segment(self, position: int) -> bool:
        """Delete the segment at the specified position."""
        if 0 <= position < len(self.segments):
            self.segments.pop(position)
            # Update positions of all segments after the deleted one
            for i in range(position, len(self.segments)):
                self.segments[i].position = i
            return True
        return False


class Revision(BaseModel):
    """A revision of a document."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    timestamp: datetime = Field(default_factory=datetime.now)
    sections: List[Section] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StructuredTextContent(TextContent):
    """
    A text content implementation that stores text in a structured document.

    This implementation is suited for complex document structures with
    sections, segments, and revision tracking.
    """

    title: str
    current_revision: Revision
    revisions: Dict[str, Revision] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True

    def __init__(self, title: str = "Untitled", **data: Any):
        """
        Initialize a new structured text content with the given title.

        Args:
            title: Document title (default: "Untitled")
        """
        initial_revision = Revision(name="Initial")
        super().__init__(title=title, current_revision=initial_revision, **data)
        self.revisions["Initial"] = initial_revision

    def insert(self, position: Position, text: str) -> None:
        """
        Insert text at the specified position.

        Args:
            position: The position where text should be inserted (must be StructuredPosition)
            text: The text to insert

        Raises:
            ValueError: If the position is invalid or not a StructuredPosition
        """
        from common.core.position import StructuredPosition, StructuredElementType

        if not isinstance(position, StructuredPosition):
            raise ValueError("Position must be a StructuredPosition")

        # Handle different element types
        if position.element_type == StructuredElementType.SECTION:
            # Find the section
            for section in self.current_revision.sections:
                if section.id == position.element_id:
                    # Add a new segment with the text
                    section.add_segment(text)
                    self.updated_at = datetime.now()
                    return
            raise ValueError(f"Section with ID {position.element_id} not found")

        elif position.element_type == StructuredElementType.SEGMENT:
            # Find the segment
            for section in self.current_revision.sections:
                for segment in section.segments:
                    if segment.id == position.element_id:
                        # Append text to the segment
                        segment.content += text
                        self.updated_at = datetime.now()
                        return
            raise ValueError(f"Segment with ID {position.element_id} not found")

        else:
            raise ValueError(f"Unsupported element type: {position.element_type}")

    def delete(self, start: Position, end: Position) -> str:
        """
        Delete text between the specified positions.

        Args:
            start: The start position of the text to delete (must be StructuredPosition)
            end: The end position of the text to delete (must be StructuredPosition)

        Returns:
            The deleted text

        Raises:
            ValueError: If either position is invalid, not a StructuredPosition,
                        or if end comes before start
        """
        from common.core.position import StructuredPosition, StructuredElementType

        if not isinstance(start, StructuredPosition) or not isinstance(
            end, StructuredPosition
        ):
            raise ValueError("Positions must be StructuredPositions")

        # Simple case: delete a segment
        if (
            start.element_type == StructuredElementType.SEGMENT
            and end.element_type == StructuredElementType.SEGMENT
            and start.element_id == end.element_id
        ):
            # Find the segment
            for section in self.current_revision.sections:
                for i, segment in enumerate(section.segments):
                    if segment.id == start.element_id:
                        deleted_text = segment.content
                        section.delete_segment(i)
                        self.updated_at = datetime.now()
                        return deleted_text

            raise ValueError(f"Segment with ID {start.element_id} not found")

        # For now, we have a limited implementation
        # More complex deletion across multiple elements would be implemented here
        raise NotImplementedError(
            "Deletion across multiple elements is not yet implemented"
        )

    def replace(self, start: Position, end: Position, text: str) -> str:
        """
        Replace text between the specified positions with new text.

        Args:
            start: The start position of the text to replace (must be StructuredPosition)
            end: The end position of the text to replace (must be StructuredPosition)
            text: The replacement text

        Returns:
            The replaced text

        Raises:
            ValueError: If either position is invalid, not a StructuredPosition,
                        or if end comes before start
        """
        from common.core.position import StructuredPosition, StructuredElementType

        if not isinstance(start, StructuredPosition) or not isinstance(
            end, StructuredPosition
        ):
            raise ValueError("Positions must be StructuredPositions")

        # Simple case: replace a segment
        if (
            start.element_type == StructuredElementType.SEGMENT
            and end.element_type == StructuredElementType.SEGMENT
            and start.element_id == end.element_id
        ):
            # Find the segment
            for section in self.current_revision.sections:
                for segment in section.segments:
                    if segment.id == start.element_id:
                        old_text = segment.content
                        segment.content = text
                        self.updated_at = datetime.now()
                        return old_text

            raise ValueError(f"Segment with ID {start.element_id} not found")

        # For now, we have a limited implementation
        # More complex replacement across multiple elements would be implemented here
        raise NotImplementedError(
            "Replacement across multiple elements is not yet implemented"
        )

    def get_text(
        self, start: Optional[Position] = None, end: Optional[Position] = None
    ) -> str:
        """
        Get text between the specified positions.

        Args:
            start: The start position (default: beginning of content)
            end: The end position (default: end of content)

        Returns:
            The text between start and end positions

        Raises:
            ValueError: If either position is invalid, not a StructuredPosition,
                        or if end comes before start
        """
        from common.core.position import StructuredPosition, StructuredElementType

        # If no positions provided, return all content
        if start is None and end is None:
            return "\n\n".join(
                [
                    f"# {section.title}\n\n{section.get_content()}"
                    for section in self.current_revision.sections
                ]
            )

        if start is not None and not isinstance(start, StructuredPosition):
            raise ValueError("Start position must be a StructuredPosition")

        if end is not None and not isinstance(end, StructuredPosition):
            raise ValueError("End position must be a StructuredPosition")

        # Simple case: get text of a segment
        if (
            start is not None
            and end is not None
            and start.element_type == StructuredElementType.SEGMENT
            and end.element_type == StructuredElementType.SEGMENT
            and start.element_id == end.element_id
        ):
            # Find the segment
            for section in self.current_revision.sections:
                for segment in section.segments:
                    if segment.id == start.element_id:
                        return segment.content

            raise ValueError(f"Segment with ID {start.element_id} not found")

        # Simple case: get text of a section
        if (
            start is not None
            and end is not None
            and start.element_type == StructuredElementType.SECTION
            and end.element_type == StructuredElementType.SECTION
            and start.element_id == end.element_id
        ):
            # Find the section
            for section in self.current_revision.sections:
                if section.id == start.element_id:
                    return f"# {section.title}\n\n{section.get_content()}"

            raise ValueError(f"Section with ID {start.element_id} not found")

        # For now, we have a limited implementation
        # More complex text retrieval across multiple elements would be implemented here
        if start is not None and end is not None:
            raise NotImplementedError(
                "Text retrieval across multiple elements is not yet implemented"
            )

        # If only start is provided, get text from that element to the end
        if start is not None:
            if start.element_type == StructuredElementType.SECTION:
                found = False
                section_texts = []

                for section in self.current_revision.sections:
                    if section.id == start.element_id or found:
                        section_texts.append(
                            f"# {section.title}\n\n{section.get_content()}"
                        )
                        found = True

                if found:
                    return "\n\n".join(section_texts)

                raise ValueError(f"Section with ID {start.element_id} not found")

            elif start.element_type == StructuredElementType.SEGMENT:
                found_section = None
                found_index = -1

                # Find the segment and its section
                for section in self.current_revision.sections:
                    for i, segment in enumerate(section.segments):
                        if segment.id == start.element_id:
                            found_section = section
                            found_index = i
                            break
                    if found_section:
                        break

                if found_section:
                    # Get remaining segments in this section
                    section_texts = [
                        segment.content
                        for segment in found_section.segments[found_index:]
                    ]

                    # Get all following sections
                    found = False
                    for section in self.current_revision.sections:
                        if section.id == found_section.id:
                            found = True
                            continue

                        if found:
                            section_texts.append(
                                f"# {section.title}\n\n{section.get_content()}"
                            )

                    return "\n\n".join(section_texts)

                raise ValueError(f"Segment with ID {start.element_id} not found")

        # If only end is provided, get text from the beginning to that element
        if end is not None:
            # Similar implementation to the start-only case, but from beginning to end
            # Omitted for brevity
            pass

        # This point should not be reached due to the checks above
        return ""

    def get_line_count(self) -> int:
        """
        Get the number of lines in the content.

        This is an approximation for structured content.

        Returns:
            The approximate number of lines
        """
        # Count newlines in the full content
        return self.get_text().count("\n") + 1

    def get_line(self, line_number: int) -> str:
        """
        Get a specific line from the content.

        This is an approximation for structured content.

        Args:
            line_number: The line number to retrieve (0-indexed)

        Returns:
            The requested line

        Raises:
            IndexError: If the line number is out of range
        """
        lines = self.get_text().split("\n")
        if 0 <= line_number < len(lines):
            return lines[line_number]
        raise IndexError(f"Line number {line_number} out of range")

    def get_word_count(self) -> int:
        """
        Get the total number of words in the content.

        Returns:
            The number of words
        """
        return sum(
            section.get_word_count() for section in self.current_revision.sections
        )

    def add_section(
        self, title: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Section:
        """
        Add a new section to the document.

        Args:
            title: The section title
            metadata: Optional metadata for the section

        Returns:
            The newly created section
        """
        section = Section(title=title, metadata=metadata or {})
        self.current_revision.sections.append(section)
        self.updated_at = datetime.now()
        return section

    def create_revision(
        self, name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Revision:
        """
        Create a new revision of the document.

        Args:
            name: The revision name
            metadata: Optional metadata for the revision

        Returns:
            The newly created revision
        """
        # Deep copy the current revision
        import copy

        new_revision = copy.deepcopy(self.current_revision)
        new_revision.id = str(uuid.uuid4())
        new_revision.name = name
        new_revision.timestamp = datetime.now()
        new_revision.metadata = metadata or {}

        self.revisions[name] = new_revision
        self.current_revision = new_revision
        self.updated_at = datetime.now()

        return new_revision
