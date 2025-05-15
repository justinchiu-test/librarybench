"""
Cursor implementation for the text editor.

This implementation uses the common library's LineColumnPosition.
"""

from typing import Tuple
from pydantic import BaseModel, Field

from common.core.position import LineColumnPosition
from text_editor.core.buffer import TextBuffer


class Cursor(BaseModel):
    """
    Represents a cursor position within a text buffer.

    The cursor tracks the current position in the buffer and provides methods
    for moving the cursor and ensuring it remains within valid bounds.
    """

    line: int = 0
    column: int = 0
    buffer: TextBuffer = Field(default_factory=TextBuffer)

    def move_to(self, line: int, column: int) -> None:
        """
        Move the cursor to the specified position.

        Args:
            line: Target line number (0-indexed)
            column: Target column number (0-indexed)

        Raises:
            IndexError: If the position is invalid
        """
        position = LineColumnPosition(line=line, column=column)

        if not position.is_valid(self.buffer):
            if not (0 <= line < self.buffer.get_line_count()):
                raise IndexError(f"Line number {line} out of range")
            else:
                line_length = len(self.buffer.get_line(line))
                raise IndexError(f"Column number {column} out of range for line {line}")

        self.line = line
        self.column = column

    def get_position(self) -> Tuple[int, int]:
        """
        Get the current cursor position.

        Returns:
            A tuple of (line, column)
        """
        return (self.line, self.column)

    def move_up(self, count: int = 1) -> None:
        """
        Move the cursor up by the specified number of lines.

        Args:
            count: Number of lines to move up (default: 1)
        """
        target_line = max(0, self.line - count)
        # Ensure column is valid in the new line
        target_column = min(self.column, len(self.buffer.get_line(target_line)))
        self.move_to(target_line, target_column)

    def move_down(self, count: int = 1) -> None:
        """
        Move the cursor down by the specified number of lines.

        Args:
            count: Number of lines to move down (default: 1)
        """
        target_line = min(self.buffer.get_line_count() - 1, self.line + count)
        # Ensure column is valid in the new line
        target_column = min(self.column, len(self.buffer.get_line(target_line)))
        self.move_to(target_line, target_column)

    def move_left(self, count: int = 1) -> None:
        """
        Move the cursor left by the specified number of characters.

        If the cursor is at the beginning of a line, it will move to the
        end of the previous line.

        Args:
            count: Number of characters to move left (default: 1)
        """
        remaining_moves = count

        while remaining_moves > 0:
            if self.column > 0:
                # We can move left within the current line
                move_amount = min(remaining_moves, self.column)
                self.column -= move_amount
                remaining_moves -= move_amount
            elif self.line > 0:
                # Move to the end of the previous line
                self.line -= 1
                self.column = len(self.buffer.get_line(self.line))
                remaining_moves -= 1
            else:
                # Already at the start of the buffer
                break

    def move_right(self, count: int = 1) -> None:
        """
        Move the cursor right by the specified number of characters.

        If the cursor is at the end of a line, it will move to the
        beginning of the next line.

        Args:
            count: Number of characters to move right (default: 1)
        """
        remaining_moves = count

        while remaining_moves > 0:
            current_line_length = len(self.buffer.get_line(self.line))

            if self.column < current_line_length:
                # We can move right within the current line
                move_amount = min(remaining_moves, current_line_length - self.column)
                self.column += move_amount
                remaining_moves -= move_amount
            elif self.line < self.buffer.get_line_count() - 1:
                # Move to the beginning of the next line
                self.line += 1
                self.column = 0
                remaining_moves -= 1
            else:
                # Already at the end of the buffer
                break

    def move_to_line_start(self) -> None:
        """Move the cursor to the start of the current line."""
        self.column = 0

    def move_to_line_end(self) -> None:
        """Move the cursor to the end of the current line."""
        self.column = len(self.buffer.get_line(self.line))

    def move_to_buffer_start(self) -> None:
        """Move the cursor to the start of the buffer."""
        self.line = 0
        self.column = 0

    def move_to_buffer_end(self) -> None:
        """Move the cursor to the end of the buffer."""
        self.line = self.buffer.get_line_count() - 1
        self.column = len(self.buffer.get_line(self.line))

    def to_position(self) -> LineColumnPosition:
        """
        Convert the cursor to a LineColumnPosition.

        Returns:
            A LineColumnPosition representing the cursor position
        """
        return LineColumnPosition(line=self.line, column=self.column)
