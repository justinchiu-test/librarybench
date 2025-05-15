"""
File management functionality for the text editor.

This implementation uses the common library's FileManager.
"""

from typing import Optional
from pydantic import BaseModel
import time
import os

from common.core.file_manager import FileManager as BaseFileManager


class FileManager(BaseFileManager):
    """
    Manages file operations for the text editor.

    This class extends the common library's FileManager to maintain
    backward compatibility with the original FileManager.
    """

    def load_file(self, file_path: str) -> str:
        """
        Load content from a file.

        Args:
            file_path: Path to the file to load

        Returns:
            The file content as a string

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If the file cannot be read
        """
        return super().load_file(file_path)

    def save_file(self, content: str, file_path: Optional[str] = None) -> None:
        """
        Save content to a file.

        Args:
            content: The content to save
            file_path: Path to save to (if None, uses current_path)

        Raises:
            ValueError: If no file path is provided and no current path is set
            PermissionError: If the file cannot be written
        """
        super().save_file(content, file_path)

    def is_file_modified(self, file_path: Optional[str] = None) -> bool:
        """
        Check if the file has been modified since it was last saved.

        Args:
            file_path: Path to check (if None, uses current_path)

        Returns:
            True if the file has been modified, False otherwise

        Raises:
            ValueError: If no file path is provided and no current path is set
        """
        return super().is_file_modified(file_path)

    def get_current_path(self) -> Optional[str]:
        """
        Get the current file path.

        Returns:
            The current file path, or None if no file is open
        """
        return super().get_current_path()
