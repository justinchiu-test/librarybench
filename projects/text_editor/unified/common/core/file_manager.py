"""
File manager module for handling file I/O operations.

This module provides a FileManager class that handles loading from and saving
to files, tracking file state, and managing file-related operations.
"""

import os
import time
import json
from typing import Any, Dict, List, Optional, Tuple, Union, TYPE_CHECKING
from pydantic import BaseModel, Field

# Avoid circular import while maintaining type hints
if TYPE_CHECKING:
    from common.core.text_content import TextContent


class FileManager(BaseModel):
    """
    Manages file operations for text editors.

    This class provides functionality for loading from and saving to files,
    tracking file state, and handling file-related operations.
    """

    current_path: Optional[str] = None
    last_saved_time: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

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
            UnicodeDecodeError: If the file encoding is not supported
        """
        start_time = time.time()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.current_path = file_path
            self.last_saved_time = os.path.getmtime(file_path)

            # Store file metadata
            self.metadata["load_time_ms"] = (time.time() - start_time) * 1000
            self.metadata["file_size"] = os.path.getsize(file_path)
            self.metadata["encoding"] = "utf-8"

            return content

        except UnicodeDecodeError:
            # Try with latin-1 encoding as a fallback
            with open(file_path, "r", encoding="latin-1") as f:
                content = f.read()

            self.current_path = file_path
            self.last_saved_time = os.path.getmtime(file_path)

            # Store file metadata
            self.metadata["load_time_ms"] = (time.time() - start_time) * 1000
            self.metadata["file_size"] = os.path.getsize(file_path)
            self.metadata["encoding"] = "latin-1"

            return content

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
        start_time = time.time()

        # Use the provided path or the current path
        path = file_path or self.current_path

        if not path:
            raise ValueError("No file path provided and no current path set")

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        self.current_path = path
        self.last_saved_time = time.time()

        # Update file metadata
        self.metadata["save_time_ms"] = (time.time() - start_time) * 1000
        self.metadata["file_size"] = os.path.getsize(path)
        self.metadata["encoding"] = "utf-8"

    def save_structured_content(
        self, content: Any, file_path: Optional[str] = None, format: str = "json"
    ) -> None:
        """
        Save structured content to a file in a specified format.

        Args:
            content: The content to save (must be serializable)
            file_path: Path to save to (if None, uses current_path)
            format: The format to save in (currently only "json" is supported)

        Raises:
            ValueError: If no file path is provided and no current path is set,
                       or if the format is not supported
            PermissionError: If the file cannot be written
        """
        start_time = time.time()

        # Use the provided path or the current path
        path = file_path or self.current_path

        if not path:
            raise ValueError("No file path provided and no current path set")

        if format.lower() == "json":
            with open(path, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

        self.current_path = path
        self.last_saved_time = time.time()

        # Update file metadata
        self.metadata["save_time_ms"] = (time.time() - start_time) * 1000
        self.metadata["file_size"] = os.path.getsize(path)
        self.metadata["format"] = format

    def load_structured_content(self, file_path: str, format: str = "json") -> Any:
        """
        Load structured content from a file.

        Args:
            file_path: Path to the file to load
            format: The format of the file (currently only "json" is supported)

        Returns:
            The loaded structured content

        Raises:
            FileNotFoundError: If the file does not exist
            PermissionError: If the file cannot be read
            ValueError: If the format is not supported
            json.JSONDecodeError: If the file is not valid JSON
        """
        start_time = time.time()

        if format.lower() == "json":
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
        else:
            raise ValueError(f"Unsupported format: {format}")

        self.current_path = file_path
        self.last_saved_time = os.path.getmtime(file_path)

        # Store file metadata
        self.metadata["load_time_ms"] = (time.time() - start_time) * 1000
        self.metadata["file_size"] = os.path.getsize(file_path)
        self.metadata["format"] = format

        return content

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
        path = file_path or self.current_path

        if not path:
            raise ValueError("No file path provided and no current path set")

        if not os.path.exists(path):
            return True

        if not self.last_saved_time:
            return True

        return os.path.getmtime(path) > self.last_saved_time

    def get_file_info(self, file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about the file.

        Args:
            file_path: Path to check (if None, uses current_path)

        Returns:
            A dictionary with file information

        Raises:
            ValueError: If no file path is provided and no current path is set
        """
        path = file_path or self.current_path

        if not path:
            raise ValueError("No file path provided and no current path set")

        if not os.path.exists(path):
            return {"exists": False}

        return {
            "exists": True,
            "size": os.path.getsize(path),
            "modified_time": os.path.getmtime(path),
            "created_time": os.path.getctime(path),
            "is_directory": os.path.isdir(path),
            "file_name": os.path.basename(path),
            "directory": os.path.dirname(path),
            "extension": os.path.splitext(path)[1],
        }

    def get_current_path(self) -> Optional[str]:
        """
        Get the current file path.

        Returns:
            The current file path, or None if no file is open
        """
        return self.current_path
