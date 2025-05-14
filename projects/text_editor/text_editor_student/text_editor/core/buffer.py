"""
Text buffer implementation for the text editor.
"""
from typing import List, Tuple, Optional
from pydantic import BaseModel


class TextBuffer(BaseModel):
    """
    A text buffer that stores the content of a file as a list of lines.
    
    This is the core data structure for the text editor, handling storage,
    insertion, deletion, and retrieval of text.
    """
    lines: List[str] = []
    
    def __init__(self, content: str = ""):
        """
        Initialize a new text buffer with the given content.
        
        Args:
            content: Initial text content (defaults to empty string)
        """
        super().__init__()
        self.lines = content.split("\n") if content else [""]
    
    def get_content(self) -> str:
        """
        Get the entire content of the buffer as a string.
        
        Returns:
            The content of the buffer as a string with lines joined by newlines
        """
        return "\n".join(self.lines)
    
    def get_line(self, line_number: int) -> str:
        """
        Get a specific line from the buffer.
        
        Args:
            line_number: The line number to retrieve (0-indexed)
            
        Returns:
            The requested line as a string
            
        Raises:
            IndexError: If the line number is out of range
        """
        if 0 <= line_number < len(self.lines):
            return self.lines[line_number]
        raise IndexError(f"Line number {line_number} out of range")
    
    def get_line_count(self) -> int:
        """
        Get the total number of lines in the buffer.
        
        Returns:
            The number of lines in the buffer
        """
        return len(self.lines)
    
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
        # Ensure line is valid
        if not (0 <= line < len(self.lines)):
            raise IndexError(f"Line number {line} out of range")
        
        # Ensure column is valid
        current_line = self.lines[line]
        if not (0 <= column <= len(current_line)):
            raise IndexError(f"Column number {column} out of range for line {line}")
        
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
            self.lines[line:line+1] = new_content
        else:
            # Simple single-line insertion
            new_line = current_line[:column] + text + current_line[column:]
            self.lines[line] = new_line
    
    def delete_text(self, start_line: int, start_col: int, 
                   end_line: int, end_col: int) -> str:
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
        # Validate positions
        if start_line > end_line or (start_line == end_line and start_col > end_col):
            raise ValueError("End position must come after start position")
        
        # Ensure positions are within range
        if not (0 <= start_line < len(self.lines)):
            raise IndexError(f"Start line {start_line} out of range")
        if not (0 <= end_line < len(self.lines)):
            raise IndexError(f"End line {end_line} out of range")
        
        start_line_text = self.lines[start_line]
        end_line_text = self.lines[end_line]
        
        if not (0 <= start_col <= len(start_line_text)):
            raise IndexError(f"Start column {start_col} out of range for line {start_line}")
        if not (0 <= end_col <= len(end_line_text)):
            raise IndexError(f"End column {end_col} out of range for line {end_line}")
        
        # Handle deletion within a single line
        if start_line == end_line:
            deleted_text = start_line_text[start_col:end_col]
            self.lines[start_line] = start_line_text[:start_col] + start_line_text[end_col:]
            return deleted_text
        
        # Handle multi-line deletion
        deleted_lines = []
        
        # Get the first partial line
        deleted_lines.append(start_line_text[start_col:])
        
        # Get any full lines in the middle
        if end_line - start_line > 1:
            deleted_lines.extend(self.lines[start_line+1:end_line])
        
        # Get the last partial line
        deleted_lines.append(end_line_text[:end_col])
        
        # Join the deleted text
        deleted_text = "\n".join(deleted_lines)
        
        # Update the buffer
        new_line = start_line_text[:start_col] + end_line_text[end_col:]
        self.lines[start_line:end_line+1] = [new_line]
        
        return deleted_text
        
    def replace_text(self, start_line: int, start_col: int,
                    end_line: int, end_col: int, new_text: str) -> str:
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
        # Delete the text first and get what was deleted
        deleted_text = self.delete_text(start_line, start_col, end_line, end_col)
        
        # Insert the new text
        self.insert_text(start_line, start_col, new_text)
        
        return deleted_text
    
    def clear(self) -> None:
        """Clear the buffer, removing all content."""
        self.lines = [""]