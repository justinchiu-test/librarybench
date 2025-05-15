"""
History management for undo/redo functionality.
"""
from typing import List, Dict, Any, Callable, Optional, Tuple
from pydantic import BaseModel, Field
import time


class EditOperation(BaseModel):
    """
    Represents an editing operation that can be undone or redone.
    """
    type: str  # "insert", "delete", "replace"
    start_line: int
    start_col: int
    end_line: Optional[int] = None
    end_col: Optional[int] = None
    text: str = ""  # For insert and replace, this is the text that was inserted
    deleted_text: str = ""  # For delete and replace, this is the text that was deleted
    timestamp: float = Field(default_factory=time.time)


class History(BaseModel):
    """
    Manages the history of editing operations for undo/redo functionality.
    """
    undo_stack: List[EditOperation] = Field(default_factory=list)
    redo_stack: List[EditOperation] = Field(default_factory=list)
    max_history_size: int = 1000
    
    def record_insert(self, line: int, col: int, text: str) -> None:
        """
        Record an insert operation.
        
        Args:
            line: Line where text was inserted
            col: Column where text was inserted
            text: Text that was inserted
        """
        operation = EditOperation(
            type="insert",
            start_line=line,
            start_col=col,
            text=text
        )
        
        self._add_to_undo_stack(operation)
    
    def record_delete(self, start_line: int, start_col: int, 
                     end_line: int, end_col: int, deleted_text: str) -> None:
        """
        Record a delete operation.
        
        Args:
            start_line: Starting line of deleted text
            start_col: Starting column of deleted text
            end_line: Ending line of deleted text
            end_col: Ending column of deleted text
            deleted_text: The text that was deleted
        """
        operation = EditOperation(
            type="delete",
            start_line=start_line,
            start_col=start_col,
            end_line=end_line,
            end_col=end_col,
            deleted_text=deleted_text
        )
        
        self._add_to_undo_stack(operation)
    
    def record_replace(self, start_line: int, start_col: int,
                      end_line: int, end_col: int, 
                      new_text: str, deleted_text: str) -> None:
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
        operation = EditOperation(
            type="replace",
            start_line=start_line,
            start_col=start_col,
            end_line=end_line,
            end_col=end_col,
            text=new_text,
            deleted_text=deleted_text
        )
        
        self._add_to_undo_stack(operation)
    
    def _add_to_undo_stack(self, operation: EditOperation) -> None:
        """
        Add an operation to the undo stack and clear the redo stack.
        
        Args:
            operation: The operation to add
        """
        self.undo_stack.append(operation)
        self.redo_stack = []  # Clear redo stack when a new edit is made
        
        # Limit history size
        if len(self.undo_stack) > self.max_history_size:
            self.undo_stack.pop(0)
    
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
    
    def undo(self) -> Optional[EditOperation]:
        """
        Get the last operation for undoing.
        
        Returns:
            The operation to undo, or None if there are no operations to undo
        """
        if not self.can_undo():
            return None
        
        operation = self.undo_stack.pop()
        self.redo_stack.append(operation)
        return operation
    
    def redo(self) -> Optional[EditOperation]:
        """
        Get the last undone operation for redoing.
        
        Returns:
            The operation to redo, or None if there are no operations to redo
        """
        if not self.can_redo():
            return None
        
        operation = self.redo_stack.pop()
        self.undo_stack.append(operation)
        return operation
    
    def clear(self) -> None:
        """Clear all history."""
        self.undo_stack = []
        self.redo_stack = []