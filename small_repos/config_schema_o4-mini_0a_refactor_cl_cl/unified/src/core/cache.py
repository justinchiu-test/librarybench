"""Configuration cache with timestamp validation."""
import os
import time
import threading
from typing import Dict, Any, Optional, Tuple, Union


class ConfigCache:
    """Thread-safe cache for configuration files."""
    
    def __init__(self):
        """Initialize an empty cache."""
        self._cache = {}  # file_path -> (timestamp, config)
        self._lock = threading.RLock()
        
    def get(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get a cached configuration if it's still valid.
        
        Args:
            file_path: Path to the configuration file
            
        Returns:
            The cached configuration, or None if not cached or invalid
        """
        with self._lock:
            if file_path not in self._cache:
                return None
                
            timestamp, config = self._cache[file_path]
            
            # Check if the file has been modified
            try:
                current_timestamp = os.path.getmtime(file_path)
                if current_timestamp > timestamp:
                    # File has been modified, invalidate cache
                    return None
                    
                # Cache is still valid
                return config
            except OSError:
                # File doesn't exist anymore
                del self._cache[file_path]
                return None
                
    def set(self, file_path: str, config: Dict[str, Any]) -> None:
        """Cache a configuration with the current timestamp.
        
        Args:
            file_path: Path to the configuration file
            config: The configuration to cache
        """
        with self._lock:
            try:
                timestamp = os.path.getmtime(file_path)
                self._cache[file_path] = (timestamp, config)
            except OSError:
                # Don't cache if the file doesn't exist
                pass
                
    def invalidate(self, file_path: str) -> None:
        """Invalidate a cached configuration.
        
        Args:
            file_path: Path to the configuration file
        """
        with self._lock:
            if file_path in self._cache:
                del self._cache[file_path]
                
    def clear(self) -> None:
        """Clear the entire cache."""
        with self._lock:
            self._cache.clear()
            
    def copy(self) -> Dict[str, Tuple[float, Dict[str, Any]]]:
        """Create a copy of the cache.
        
        Returns:
            A copy of the cache dictionary
        """
        with self._lock:
            return self._cache.copy()