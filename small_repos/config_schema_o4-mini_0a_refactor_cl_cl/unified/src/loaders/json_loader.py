"""JSON file format loader."""
import json
import os
from typing import Dict, Any

from .base import ConfigLoader


class JSONLoader(ConfigLoader):
    """Loader for JSON configuration files."""

    def can_load(self, file_path: str) -> bool:
        """Check if this loader can handle JSON files.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            True if the file has a .json extension, False otherwise
        """
        return file_path.lower().endswith('.json')
        
    def load(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from a JSON file.
        
        Args:
            file_path: Path to the JSON configuration file
            
        Returns:
            Dictionary containing the configuration data
            
        Raises:
            FileNotFoundError: If the file does not exist
            json.JSONDecodeError: If the JSON content is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            return json.load(f)