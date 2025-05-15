"""YAML file format loader with graceful fallback."""
import os
from typing import Dict, Any, Optional

from .base import ConfigLoader

try:
    import yaml
except ImportError:
    yaml = None


class YAMLLoader(ConfigLoader):
    """Loader for YAML configuration files."""

    def can_load(self, file_path: str) -> bool:
        """Check if this loader can handle YAML files.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            True if the file has a .yaml or .yml extension, False otherwise
        """
        lower_path = file_path.lower()
        return lower_path.endswith('.yaml') or lower_path.endswith('.yml')
        
    def load(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from a YAML file.
        
        Args:
            file_path: Path to the YAML configuration file
            
        Returns:
            Dictionary containing the configuration data
            
        Raises:
            FileNotFoundError: If the file does not exist
            RuntimeError: If PyYAML is not available
            yaml.YAMLError: If the YAML content is invalid
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        if yaml is None:
            raise RuntimeError(
                "PyYAML is not installed. Please install it with: pip install pyyaml"
            )
        
        with open(file_path, 'r') as f:
            return yaml.safe_load(f) or {}