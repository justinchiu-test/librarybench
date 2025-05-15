"""Base loader interface for configuration files."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class ConfigLoader(ABC):
    """Abstract base class for configuration loaders."""
    
    @abstractmethod
    def can_load(self, file_path: str) -> bool:
        """Check if this loader can handle the given file path.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            True if this loader can handle the file, False otherwise
        """
        pass
    
    @abstractmethod
    def load(self, file_path: str) -> Dict[str, Any]:
        """Load configuration from a file.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            Dictionary containing the configuration data
            
        Raises:
            FileNotFoundError: If the file does not exist
            IOError: If the file cannot be read
            ValueError: If the file content is invalid
        """
        pass