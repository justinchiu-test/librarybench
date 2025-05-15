"""
History module for tracking and managing editing operations.

This module provides classes for recording, undoing, and redoing operations
on text content, supporting both simple and complex editing scenarios.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import time
from typing import Dict, List, Optional, Tuple, Union, Any, TYPE_CHECKING
from pydantic import BaseModel, Field

# Avoid circular import while maintaining type hints
if TYPE_CHECKING:
    from common.core.text_content import TextContent
    from common.core.position import Position


class Operation(BaseModel, ABC):
    """
    Abstract base class for operations that can be applied, undone, and redone.

    Operations represent atomic changes to text content that can be
    tracked, undone, and redone by a history system.
    """

    timestamp: float = Field(default_factory=time.time)

    @abstractmethod
    def apply(self, content: TextContent) -> None:
        """
        Apply this operation to the given content.

        Args:
            content: The text content to modify
        """
        pass

    @abstractmethod
    def undo(self, content: TextContent) -> None:
        """
        Undo this operation on the given content.

        Args:
            content: The text content to modify
        """
        pass


class InsertOperation(Operation):
    """
    An operation that inserts text at a specified position.
    """

    position: Dict[str, Any]  # Serialized position
    text: str

    @property
    def type(self) -> str:
        """Type of the operation for compatibility with original History."""
        return "insert"

    def apply(self, content: TextContent) -> None:
        """
        Apply this operation to the given content.

        Args:
            content: The text content to modify
        """
        from common.core.position import LineColumnPosition, StructuredPosition

        # Deserialize position based on type
        if "line" in self.position and "column" in self.position:
            position = LineColumnPosition(
                line=self.position["line"], column=self.position["column"]
            )
        else:
            position = StructuredPosition(**self.position)

        content.insert(position, self.text)

    def undo(self, content: TextContent) -> None:
        """
        Undo this operation on the given content.

        Args:
            content: The text content to modify
        """
        from common.core.position import LineColumnPosition, StructuredPosition

        # Deserialize position based on type
        if "line" in self.position and "column" in self.position:
            start_position = LineColumnPosition(
                line=self.position["line"], column=self.position["column"]
            )

            # Calculate end position based on inserted text
            lines = self.text.split("\n")
            if len(lines) == 1:
                # Single-line insertion
                end_position = LineColumnPosition(
                    line=self.position["line"],
                    column=self.position["column"] + len(self.text),
                )
            else:
                # Multi-line insertion
                end_position = LineColumnPosition(
                    line=self.position["line"] + len(lines) - 1, column=len(lines[-1])
                )
        else:
            # For structured positions, we can only undo by position
            # This is a simplification; real implementation would need more context
            start_position = StructuredPosition(**self.position)
            end_position = start_position

        content.delete(start_position, end_position)


class DeleteOperation(Operation):
    """
    An operation that deletes text between specified positions.
    """

    start_position: Dict[str, Any]  # Serialized start position
    end_position: Dict[str, Any]  # Serialized end position
    deleted_text: str

    @property
    def type(self) -> str:
        """Type of the operation for compatibility with original History."""
        return "delete"

    def apply(self, content: TextContent) -> None:
        """
        Apply this operation to the given content.

        Args:
            content: The text content to modify
        """
        from common.core.position import LineColumnPosition, StructuredPosition

        # Deserialize positions based on type
        if "line" in self.start_position and "column" in self.start_position:
            start_position = LineColumnPosition(
                line=self.start_position["line"], column=self.start_position["column"]
            )
            end_position = LineColumnPosition(
                line=self.end_position["line"], column=self.end_position["column"]
            )
        else:
            start_position = StructuredPosition(**self.start_position)
            end_position = StructuredPosition(**self.end_position)

        content.delete(start_position, end_position)

    def undo(self, content: TextContent) -> None:
        """
        Undo this operation on the given content.

        Args:
            content: The text content to modify
        """
        from common.core.position import LineColumnPosition, StructuredPosition

        # Deserialize position based on type
        if "line" in self.start_position and "column" in self.start_position:
            position = LineColumnPosition(
                line=self.start_position["line"], column=self.start_position["column"]
            )
        else:
            position = StructuredPosition(**self.start_position)

        content.insert(position, self.deleted_text)


class ReplaceOperation(Operation):
    """
    An operation that replaces text between specified positions with new text.
    """

    start_position: Dict[str, Any]  # Serialized start position
    end_position: Dict[str, Any]  # Serialized end position
    new_text: str
    old_text: str

    @property
    def type(self) -> str:
        """Type of the operation for compatibility with original History."""
        return "replace"

    def apply(self, content: TextContent) -> None:
        """
        Apply this operation to the given content.

        Args:
            content: The text content to modify
        """
        from common.core.position import LineColumnPosition, StructuredPosition

        # Deserialize positions based on type
        if "line" in self.start_position and "column" in self.start_position:
            start_position = LineColumnPosition(
                line=self.start_position["line"], column=self.start_position["column"]
            )
            end_position = LineColumnPosition(
                line=self.end_position["line"], column=self.end_position["column"]
            )
        else:
            start_position = StructuredPosition(**self.start_position)
            end_position = StructuredPosition(**self.end_position)

        content.replace(start_position, end_position, self.new_text)

    def undo(self, content: TextContent) -> None:
        """
        Undo this operation on the given content.

        Args:
            content: The text content to modify
        """
        from common.core.position import LineColumnPosition, StructuredPosition

        # Deserialize positions based on type
        if "line" in self.start_position and "column" in self.start_position:
            start_position = LineColumnPosition(
                line=self.start_position["line"], column=self.start_position["column"]
            )

            # Calculate end position based on new text
            lines = self.new_text.split("\n")
            if len(lines) == 1:
                # Single-line replacement
                end_position = LineColumnPosition(
                    line=self.start_position["line"],
                    column=self.start_position["column"] + len(self.new_text),
                )
            else:
                # Multi-line replacement
                end_position = LineColumnPosition(
                    line=self.start_position["line"] + len(lines) - 1,
                    column=len(lines[-1]),
                )
        else:
            # For structured positions, we use the original end position
            start_position = StructuredPosition(**self.start_position)
            end_position = StructuredPosition(**self.end_position)

        content.replace(start_position, end_position, self.old_text)


class History(BaseModel):
    """
    Tracks and manages the history of operations for undo/redo functionality.
    """

    undo_stack: List[Operation] = Field(default_factory=list)
    redo_stack: List[Operation] = Field(default_factory=list)
    max_history_size: int = 1000

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True

    def record_operation(self, operation: Operation) -> None:
        """
        Record an operation in the history.

        Args:
            operation: The operation to record
        """
        self.undo_stack.append(operation)
        self.redo_stack.clear()  # Clear redo stack when a new operation is recorded

        # Limit history size
        if len(self.undo_stack) > self.max_history_size:
            self.undo_stack.pop(0)

    def undo(self, content: TextContent) -> bool:
        """
        Undo the last operation on the given content.

        Args:
            content: The text content to modify

        Returns:
            True if an operation was undone, False otherwise
        """
        if not self.undo_stack:
            return False

        operation = self.undo_stack.pop()
        operation.undo(content)
        self.redo_stack.append(operation)
        return True

    def redo(self, content: TextContent) -> bool:
        """
        Redo the last undone operation on the given content.

        Args:
            content: The text content to modify

        Returns:
            True if an operation was redone, False otherwise
        """
        if not self.redo_stack:
            return False

        operation = self.redo_stack.pop()
        operation.apply(content)
        self.undo_stack.append(operation)
        return True

    def can_undo(self) -> bool:
        """
        Check if there are operations that can be undone.

        Returns:
            True if undo is possible, False otherwise
        """
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """
        Check if there are operations that can be redone.

        Returns:
            True if redo is possible, False otherwise
        """
        return len(self.redo_stack) > 0

    def clear(self) -> None:
        """Clear all history."""
        self.undo_stack.clear()
        self.redo_stack.clear()

    @staticmethod
    def create_insert_operation(position: Position, text: str) -> InsertOperation:
        """
        Create an insert operation.

        Args:
            position: The position where text was inserted
            text: The text that was inserted

        Returns:
            An InsertOperation instance
        """
        from common.core.position import LineColumnPosition, StructuredPosition

        # Serialize position based on type
        if isinstance(position, LineColumnPosition):
            position_dict = {"line": position.line, "column": position.column}
        elif isinstance(position, StructuredPosition):
            position_dict = position.dict()
        else:
            raise ValueError(f"Unsupported position type: {type(position)}")

        return InsertOperation(position=position_dict, text=text)

    @staticmethod
    def create_delete_operation(
        start: Position, end: Position, deleted_text: str
    ) -> DeleteOperation:
        """
        Create a delete operation.

        Args:
            start: The start position of deleted text
            end: The end position of deleted text
            deleted_text: The text that was deleted

        Returns:
            A DeleteOperation instance
        """
        from common.core.position import LineColumnPosition, StructuredPosition

        # Serialize positions based on type
        if isinstance(start, LineColumnPosition) and isinstance(
            end, LineColumnPosition
        ):
            start_dict = {"line": start.line, "column": start.column}
            end_dict = {"line": end.line, "column": end.column}
        elif isinstance(start, StructuredPosition) and isinstance(
            end, StructuredPosition
        ):
            start_dict = start.dict()
            end_dict = end.dict()
        else:
            raise ValueError(f"Unsupported position types: {type(start)}, {type(end)}")

        return DeleteOperation(
            start_position=start_dict, end_position=end_dict, deleted_text=deleted_text
        )

    @staticmethod
    def create_replace_operation(
        start: Position, end: Position, new_text: str, old_text: str
    ) -> ReplaceOperation:
        """
        Create a replace operation.

        Args:
            start: The start position of replaced text
            end: The end position of replaced text
            new_text: The text that was inserted
            old_text: The text that was replaced

        Returns:
            A ReplaceOperation instance
        """
        from common.core.position import LineColumnPosition, StructuredPosition

        # Serialize positions based on type
        if isinstance(start, LineColumnPosition) and isinstance(
            end, LineColumnPosition
        ):
            start_dict = {"line": start.line, "column": start.column}
            end_dict = {"line": end.line, "column": end.column}
        elif isinstance(start, StructuredPosition) and isinstance(
            end, StructuredPosition
        ):
            start_dict = start.dict()
            end_dict = end.dict()
        else:
            raise ValueError(f"Unsupported position types: {type(start)}, {type(end)}")

        return ReplaceOperation(
            start_position=start_dict,
            end_position=end_dict,
            new_text=new_text,
            old_text=old_text,
        )
