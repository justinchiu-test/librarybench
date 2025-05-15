"""TOML file format loader with graceful fallback."""
import os
from typing import Dict, Any, Optional

from .base import ConfigLoader

try:
    import toml
except ImportError:
    toml = None


class TOMLLoader(ConfigLoader):
    """Loader for TOML configuration files."""

    def can_load(self, file_path: str) -> bool:
        """Check if this loader can handle TOML files.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            True if the file has a .toml extension, False otherwise
        """
        return file_path.lower().endswith('.toml')
        
    def load(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from a TOML file.
        
        Args:
            file_path: Path to the TOML configuration file
            
        Returns:
            Dictionary containing the configuration data
            
        Raises:
            FileNotFoundError: If the file does not exist
            RuntimeError: If toml is not available
            toml.TomlDecodeError: If the TOML content is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        if toml is None:
            raise RuntimeError(
                "toml is not installed. Please install it with: pip install toml"
            )
        
        with open(file_path, 'r') as f:
            return toml.load(f)