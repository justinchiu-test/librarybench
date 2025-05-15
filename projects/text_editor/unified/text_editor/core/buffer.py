"""
Text buffer implementation for the text editor.

This implementation uses the common library's LineBasedTextContent.
"""

from typing import List, Tuple, Optional
from pydantic import BaseModel

from common.core.text_content import LineBasedTextContent
from common.core.position import LineColumnPosition


class TextBuffer(LineBasedTextContent):
    """
    A text buffer that stores the content of a file as a list of lines.

    This is the core data structure for the text editor, handling storage,
    insertion, deletion, and retrieval of text.
    """

    def __init__(self, content: str = ""):
        """
        Initialize a new text buffer with the given content.

        Args:
            content: Initial text content (defaults to empty string)
        """
        super().__init__(content=content)

    def get_content(self) -> str:
        """
        Get the entire content of the buffer as a string.

        Returns:
            The content of the buffer as a string with lines joined by newlines
        """
        return self.get_text()

    def insert_text(self, line: int, column: int, text: str) -> None:
        """
        Insert text at the specified position in the buffer.

        Args:
            line: Line number where text should be inserted (0-indexed)
            column: Column number where text should be inserted (0-indexed)
            text: The text to insert

        Raises:
            IndexError: If the line or column is out of range
        """
        position = LineColumnPosition(line=line, column=column)

        try:
            self.insert(position, text)
        except ValueError as e:
            # Convert ValueError to IndexError for backward compatibility
            raise IndexError(str(e))

    def delete_text(
        self, start_line: int, start_col: int, end_line: int, end_col: int
    ) -> str:
        """
        Delete text between the specified positions and return the deleted text.

        Args:
            start_line: Starting line number (0-indexed)
            start_col: Starting column number (0-indexed)
            end_line: Ending line number (0-indexed)
            end_col: Ending column number (0-indexed)

        Returns:
            The deleted text

        Raises:
            IndexError: If any position is out of range
            ValueError: If the end position comes before the start position
        """
        start_position = LineColumnPosition(line=start_line, column=start_col)
        end_position = LineColumnPosition(line=end_line, column=end_col)

        try:
            return self.delete(start_position, end_position)
        except ValueError as e:
            # Convert ValueError to appropriate error for backward compatibility
            if "End position must come after start position" in str(e):
                raise ValueError(str(e))
            else:
                raise IndexError(str(e))

    def replace_text(
        self,
        start_line: int,
        start_col: int,
        end_line: int,
        end_col: int,
        new_text: str,
    ) -> str:
        """
        Replace text between the specified positions with new text.

        Args:
            start_line: Starting line number (0-indexed)
            start_col: Starting column number (0-indexed)
            end_line: Ending line number (0-indexed)
            end_col: Ending column number (0-indexed)
            new_text: The text to insert

        Returns:
            The replaced text

        Raises:
            IndexError: If any position is out of range
            ValueError: If the end position comes before the start position
        """
        start_position = LineColumnPosition(line=start_line, column=start_col)
        end_position = LineColumnPosition(line=end_line, column=end_col)

        try:
            return self.replace(start_position, end_position, new_text)
        except ValueError as e:
            # Convert ValueError to appropriate error for backward compatibility
            if "End position must come after start position" in str(e):
                raise ValueError(str(e))
            else:
                raise IndexError(str(e))

    def clear(self) -> None:
        """Clear the buffer, removing all content."""
        super().clear()
