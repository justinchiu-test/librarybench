"""
Core editor implementation that combines buffer and cursor functionality.

This implementation uses the common library's components where appropriate.
"""

from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
import time

from common.core.position import LineColumnPosition
from common.core.text_content import TextContent
from text_editor.core.buffer import TextBuffer
from text_editor.core.cursor import Cursor
from text_editor.core.file_manager import FileManager
from text_editor.core.history import History, EditOperation


class Editor(BaseModel):
    """
    Core editor class that combines buffer and cursor functionality.

    This class provides the basic editing operations that form the foundation
    of the text editor, including text insertion, deletion, navigation, and
    other fundamental operations.
    """

    buffer: TextBuffer = Field(default_factory=TextBuffer)
    cursor: Cursor = None
    file_manager: FileManager = Field(default_factory=FileManager)
    history: History = Field(default_factory=History)

    def __init__(self, content: str = "", file_path: Optional[str] = None):
        """
        Initialize a new editor with the given content.

        Args:
            content: Initial text content (defaults to empty string)
            file_path: Path to the file being edited (optional)
        """
        super().__init__()
        self.buffer = TextBuffer(content)
        self.cursor = Cursor(buffer=self.buffer)
        self.file_manager = FileManager(current_path=file_path)
        self.history = History()

    def get_content(self) -> str:
        """
        Get the entire content of the editor.

        Returns:
            The content as a string
        """
        return self.buffer.get_text()

    def get_cursor_position(self) -> Tuple[int, int]:
        """
        Get the current cursor position.

        Returns:
            A tuple of (line, column)
        """
        return self.cursor.get_position()

    def insert_text(self, text: str) -> None:
        """
        Insert text at the current cursor position.

        Args:
            text: The text to insert
        """
        line, column = self.cursor.get_position()
        position = LineColumnPosition(line=line, column=column)

        # Insert the text using the buffer
        self.buffer.insert(position, text)

        # Record the operation in history
        self.history.record_insert(line, column, text)

        # Update cursor position
        if "\n" in text:
            # Move to the end of the inserted text
            lines = text.split("\n")
            new_line = line + len(lines) - 1
            new_column = len(lines[-1])
            self.cursor.move_to(new_line, new_column)
        else:
            # Move cursor forward by the length of the inserted text
            self.cursor.move_to(line, column + len(text))

    def delete_char_before_cursor(self) -> None:
        """Delete the character before the cursor (backspace operation)."""
        line, column = self.cursor.get_position()

        if column > 0:
            # Delete character in the current line
            start_position = LineColumnPosition(line=line, column=column - 1)
            end_position = LineColumnPosition(line=line, column=column)

            deleted_text = self.buffer.delete(start_position, end_position)
            self.history.record_delete(line, column - 1, line, column, deleted_text)
            self.cursor.move_to(line, column - 1)
        elif line > 0:
            # At the beginning of a line, join with the previous line
            prev_line_length = len(self.buffer.get_line(line - 1))

            start_position = LineColumnPosition(line=line - 1, column=prev_line_length)
            end_position = LineColumnPosition(line=line, column=0)

            deleted_text = self.buffer.delete(start_position, end_position)
            self.history.record_delete(
                line - 1, prev_line_length, line, 0, deleted_text
            )
            self.cursor.move_to(line - 1, prev_line_length)

    def delete_char_after_cursor(self) -> None:
        """Delete the character after the cursor (delete key operation)."""
        line, column = self.cursor.get_position()
        line_length = len(self.buffer.get_line(line))

        if column < line_length:
            # Delete character in the current line
            start_position = LineColumnPosition(line=line, column=column)
            end_position = LineColumnPosition(line=line, column=column + 1)

            deleted_text = self.buffer.delete(start_position, end_position)
            self.history.record_delete(line, column, line, column + 1, deleted_text)
        elif line < self.buffer.get_line_count() - 1:
            # At the end of a line, join with the next line
            start_position = LineColumnPosition(line=line, column=line_length)
            end_position = LineColumnPosition(line=line + 1, column=0)

            deleted_text = self.buffer.delete(start_position, end_position)
            self.history.record_delete(line, line_length, line + 1, 0, deleted_text)

    def new_line(self) -> None:
        """Insert a new line at the cursor position."""
        self.insert_text("\n")

    def move_cursor(self, direction: str, count: int = 1) -> None:
        """
        Move the cursor in the specified direction.

        Args:
            direction: One of "up", "down", "left", "right",
                      "line_start", "line_end", "buffer_start", "buffer_end"
            count: Number of units to move (for up, down, left, right)
        """
        if direction == "up":
            self.cursor.move_up(count)
        elif direction == "down":
            self.cursor.move_down(count)
        elif direction == "left":
            self.cursor.move_left(count)
        elif direction == "right":
            self.cursor.move_right(count)
        elif direction == "line_start":
            self.cursor.move_to_line_start()
        elif direction == "line_end":
            self.cursor.move_to_line_end()
        elif direction == "buffer_start":
            self.cursor.move_to_buffer_start()
        elif direction == "buffer_end":
            self.cursor.move_to_buffer_end()
        else:
            raise ValueError(f"Unknown direction: {direction}")

    def set_cursor_position(self, line: int, column: int) -> None:
        """
        Set the cursor to the specified position.

        Args:
            line: Line number (0-indexed)
            column: Column number (0-indexed)
        """
        self.cursor.move_to(line, column)

    def get_line(self, line_number: int) -> str:
        """
        Get a specific line from the buffer.

        Args:
            line_number: The line number to retrieve (0-indexed)

        Returns:
            The requested line as a string
        """
        return self.buffer.get_line(line_number)

    def get_line_count(self) -> int:
        """
        Get the total number of lines in the buffer.

        Returns:
            The number of lines
        """
        return self.buffer.get_line_count()

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
        """
        start_position = LineColumnPosition(line=start_line, column=start_col)
        end_position = LineColumnPosition(line=end_line, column=end_col)

        deleted_text = self.buffer.replace(start_position, end_position, new_text)
        self.history.record_replace(
            start_line, start_col, end_line, end_col, new_text, deleted_text
        )
        return deleted_text

    def clear(self) -> None:
        """Clear the editor, removing all content."""
        content = self.buffer.get_text()
        if content:
            line_count = self.buffer.get_line_count()
            last_line_length = len(self.buffer.get_line(line_count - 1))

            start_position = LineColumnPosition(line=0, column=0)
            end_position = LineColumnPosition(
                line=line_count - 1, column=last_line_length
            )

            self.history.record_delete(0, 0, line_count - 1, last_line_length, content)

        self.buffer.clear()
        self.cursor.move_to_buffer_start()

    def undo(self) -> bool:
        """
        Undo the last operation.

        Returns:
            True if an operation was undone, False otherwise
        """
        return self.history.undo(self.buffer)

    def redo(self) -> bool:
        """
        Redo the last undone operation.

        Returns:
            True if an operation was redone, False otherwise
        """
        return self.history.redo(self.buffer)

    def load_file(self, file_path: str) -> None:
        """
        Load content from a file.

        Args:
            file_path: Path to the file to load
        """
        content = self.file_manager.load_file(file_path)
        self.buffer = TextBuffer(content)
        self.cursor = Cursor(buffer=self.buffer)
        self.history.clear()

    def save_file(self, file_path: Optional[str] = None) -> None:
        """
        Save content to a file.

        Args:
            file_path: Path to save to (if None, uses current path)
        """
        content = self.buffer.get_text()
        self.file_manager.save_file(content, file_path)

    def get_current_file_path(self) -> Optional[str]:
        """
        Get the current file path.

        Returns:
            The current file path, or None if no file is open
        """
        return self.file_manager.get_current_path()

    def is_file_modified(self) -> bool:
        """
        Check if the file has been modified since it was last saved.

        Returns:
            True if the file has been modified, False otherwise
        """
        return self.file_manager.is_file_modified()
