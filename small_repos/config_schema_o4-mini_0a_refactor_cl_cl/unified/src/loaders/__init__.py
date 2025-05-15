"""Configuration loaders for different file formats."""
from typing import Dict, Any, List, Type

from .base import ConfigLoader
from .json_loader import JSONLoader
from .ini_loader import INILoader
from .yaml_loader import YAMLLoader
from .toml_loader import TOMLLoader

# Registry of available loaders
_loaders: List[Type[ConfigLoader]] = [
    JSONLoader,
    INILoader,
    YAMLLoader,
    TOMLLoader
]


def get_loader(file_path: str) -> ConfigLoader:
    """Get an appropriate loader for a given file path.
    
    Args:
        file_path: Path to the configuration file
        
    Returns:
        An instance of a ConfigLoader that can handle this file
        
    Raises:
        ValueError: If no suitable loader is found
    """
    for loader_cls in _loaders:
        loader = loader_cls()
        if loader.can_load(file_path):
            return loader
            
    raise ValueError(f"No suitable loader found for file: {file_path}")


def load_config_file(file_path: str) -> Dict[str, Any]:
    """Load configuration from a file using the appropriate loader.
    
    Args:
        file_path: Path to the configuration file
        
    Returns:
        Dictionary containing the configuration data
        
    Raises:
        FileNotFoundError: If the file does not exist
        IOError: If the file cannot be read
        ValueError: If the file content is invalid or no suitable loader is found
    """
    loader = get_loader(file_path)
    return loader.load(file_path)