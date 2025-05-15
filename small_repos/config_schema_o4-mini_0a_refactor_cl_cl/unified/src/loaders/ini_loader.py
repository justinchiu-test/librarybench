"""INI file format loader."""
import os
import configparser
from typing import Dict, Any

from .base import ConfigLoader


class INILoader(ConfigLoader):
    """Loader for INI configuration files."""

    def can_load(self, file_path: str) -> bool:
        """Check if this loader can handle INI files.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            True if the file has a .ini extension, False otherwise
        """
        return file_path.lower().endswith('.ini')
        
    def load(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from an INI file.
        
        Args:
            file_path: Path to the INI configuration file
            
        Returns:
            Dictionary containing the configuration data
            
        Raises:
            FileNotFoundError: If the file does not exist
            configparser.Error: If the INI content is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        config = configparser.ConfigParser()
        config.read(file_path)
        
        # Convert to dictionary
        result = {}
        for section in config.sections():
            result[section] = dict(config[section])
        
        # Add DEFAULT section if it has values
        if config.defaults():
            result['DEFAULT'] = dict(config.defaults())
            
        return result