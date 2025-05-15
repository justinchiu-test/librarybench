"""
History management for undo/redo functionality.

This implementation uses the common library's History class.
"""

from typing import List, Dict, Any, Callable, Optional, Tuple
from pydantic import BaseModel, Field
import time

from common.core.history import (
    History as BaseHistory,
    Operation,
    InsertOperation,
    DeleteOperation,
    ReplaceOperation,
)
from common.core.position import LineColumnPosition
from common.core.text_content import TextContent


class EditOperation(BaseModel):
    """
    Represents an editing operation that can be undone or redone.

    This class maintains backward compatibility with the original EditOperation.
    """

    type: str  # "insert", "delete", "replace"
    start_line: int
    start_col: int
    end_line: Optional[int] = None
    end_col: Optional[int] = None
    text: str = ""  # For insert and replace, this is the text that was inserted
    deleted_text: str = ""  # For delete and replace, this is the text that was deleted
    timestamp: float = Field(default_factory=time.time)

    def to_common_operation(self) -> Operation:
        """
        Convert this EditOperation to a common library Operation.

        Returns:
            A common library Operation
        """
        if self.type == "insert":
            position_dict = {"line": self.start_line, "column": self.start_col}
            return InsertOperation(position=position_dict, text=self.text)

        elif self.type == "delete":
            if self.end_line is None or self.end_col is None:
                raise ValueError("End position is required for delete operations")

            start_position_dict = {"line": self.start_line, "column": self.start_col}
            end_position_dict = {"line": self.end_line, "column": self.end_col}
            return DeleteOperation(
                start_position=start_position_dict,
                end_position=end_position_dict,
                deleted_text=self.deleted_text,
            )

        elif self.type == "replace":
            if self.end_line is None or self.end_col is None:
                raise ValueError("End position is required for replace operations")

            start_position_dict = {"line": self.start_line, "column": self.start_col}
            end_position_dict = {"line": self.end_line, "column": self.end_col}
            return ReplaceOperation(
                start_position=start_position_dict,
                end_position=end_position_dict,
                new_text=self.text,
                old_text=self.deleted_text,
            )

        else:
            raise ValueError(f"Unknown operation type: {self.type}")


class History(BaseHistory):
    """
    Manages the history of editing operations for undo/redo functionality.

    This class extends the common library's History class to maintain
    backward compatibility with the original History.
    """

    def record_insert(self, line: int, col: int, text: str) -> None:
        """
        Record an insert operation.

        Args:
            line: Line where text was inserted
            col: Column where text was inserted
            text: Text that was inserted
        """
        position = LineColumnPosition(line=line, column=col)
        operation = self.create_insert_operation(position, text)
        self.record_operation(operation)

    def record_delete(
        self,
        start_line: int,
        start_col: int,
        end_line: int,
        end_col: int,
        deleted_text: str,
    ) -> None:
        """
        Record a delete operation.

        Args:
            start_line: Starting line of deleted text
            start_col: Starting column of deleted text
            end_line: Ending line of deleted text
            end_col: Ending column of deleted text
            deleted_text: The text that was deleted
        """
        start_position = LineColumnPosition(line=start_line, column=start_col)
        end_position = LineColumnPosition(line=end_line, column=end_col)
        operation = self.create_delete_operation(
            start_position, end_position, deleted_text
        )
        self.record_operation(operation)

    def record_replace(
        self,
        start_line: int,
        start_col: int,
        end_line: int,
        end_col: int,
        new_text: str,
        deleted_text: str,
    ) -> None:
        """
        Record a replace operation.

        Args:
            start_line: Starting line of replaced text
            start_col: Starting column of replaced text
            end_line: Ending line of replaced text
            end_col: Ending column of replaced text
            new_text: The text that was inserted
            deleted_text: The text that was deleted
        """
        start_position = LineColumnPosition(line=start_line, column=start_col)
        end_position = LineColumnPosition(line=end_line, column=end_col)
        operation = self.create_replace_operation(
            start_position, end_position, new_text, deleted_text
        )
        self.record_operation(operation)

    # Add compatibility methods for the old API

    def can_undo(self) -> bool:
        """
        Check if there are operations that can be undone.

        Returns:
            True if undo is possible, False otherwise
        """
        return super().can_undo()

    def can_redo(self) -> bool:
        """
        Check if there are operations that can be redone.

        Returns:
            True if redo is possible, False otherwise
        """
        return super().can_redo()

    def undo(self, content: Optional[TextContent] = None) -> Optional[EditOperation]:
        """
        Get the last operation for undoing.

        This method maintains backward compatibility with the original History.
        If a content object is provided, it will undo the operation.

        Args:
            content: Optional content object to apply the undo to

        Returns:
            The operation to undo, or None if there are no operations to undo
        """
        if not self.can_undo():
            return None

        # Get the operation without removing it from the stack
        operation = self.undo_stack[-1]

        # If content is provided, apply the undo
        if content is not None:
            super().undo(content)
        else:
            # Just remove from the undo stack and add to redo stack without applying
            self.undo_stack.pop()
            self.redo_stack.append(operation)

        # Convert to EditOperation for backward compatibility
        if isinstance(operation, InsertOperation):
            return EditOperation(
                type="insert",
                start_line=operation.position.get("line", 0),
                start_col=operation.position.get("column", 0),
                text=operation.text,
            )
        elif isinstance(operation, DeleteOperation):
            return EditOperation(
                type="delete",
                start_line=operation.start_position.get("line", 0),
                start_col=operation.start_position.get("column", 0),
                end_line=operation.end_position.get("line", 0),
                end_col=operation.end_position.get("column", 0),
                deleted_text=operation.deleted_text,
            )
        elif isinstance(operation, ReplaceOperation):
            return EditOperation(
                type="replace",
                start_line=operation.start_position.get("line", 0),
                start_col=operation.start_position.get("column", 0),
                end_line=operation.end_position.get("line", 0),
                end_col=operation.end_position.get("column", 0),
                text=operation.new_text,
                deleted_text=operation.old_text,
            )

        return None

    def redo(self, content: Optional[TextContent] = None) -> Optional[EditOperation]:
        """
        Get the last undone operation for redoing.

        This method maintains backward compatibility with the original History.
        If a content object is provided, it will redo the operation.

        Args:
            content: Optional content object to apply the redo to

        Returns:
            The operation to redo, or None if there are no operations to redo
        """
        if not self.can_redo():
            return None

        # Get the operation without removing it from the stack
        operation = self.redo_stack[-1]

        # If content is provided, apply the redo
        if content is not None:
            super().redo(content)
        else:
            # Just remove from the redo stack and add to undo stack without applying
            self.redo_stack.pop()
            self.undo_stack.append(operation)

        # Convert to EditOperation for backward compatibility
        if isinstance(operation, InsertOperation):
            return EditOperation(
                type="insert",
                start_line=operation.position.get("line", 0),
                start_col=operation.position.get("column", 0),
                text=operation.text,
            )
        elif isinstance(operation, DeleteOperation):
            return EditOperation(
                type="delete",
                start_line=operation.start_position.get("line", 0),
                start_col=operation.start_position.get("column", 0),
                end_line=operation.end_position.get("line", 0),
                end_col=operation.end_position.get("column", 0),
                deleted_text=operation.deleted_text,
            )
        elif isinstance(operation, ReplaceOperation):
            return EditOperation(
                type="replace",
                start_line=operation.start_position.get("line", 0),
                start_col=operation.start_position.get("column", 0),
                end_line=operation.end_position.get("line", 0),
                end_col=operation.end_position.get("column", 0),
                text=operation.new_text,
                deleted_text=operation.old_text,
            )

        return None

    def clear(self) -> None:
        """Clear all history."""
        super().clear()
