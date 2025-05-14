"""
Translation cache module for translator tools.
Provides caching for translation operations to improve performance.
"""

import os
import shelve
import json
import hashlib
from typing import Any, Dict, Optional, Union


class TranslationCache:
    """
    Cache for translation operations.
    Provides both in-memory and disk-backed caching to improve performance.
    """
    
    def __init__(self, 
                cache_dir: Optional[str] = None,
                max_entries: int = 1000,
                use_memory: bool = True,
                use_disk: bool = True):
        """
        Initialize a new translation cache.
        
        Args:
            cache_dir: Directory to store cache files
            max_entries: Maximum number of in-memory cache entries
            use_memory: Whether to use in-memory caching
            use_disk: Whether to use disk-backed caching
        """
        self.max_entries = max_entries
        self.use_memory = use_memory
        self.use_disk = use_disk
        
        # Setup cache directory
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            # Default to a directory in the user's home
            self.cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "translator")
        
        # Create cache directory if it doesn't exist
        if self.use_disk and not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
        
        # Initialize in-memory cache
        self.memory_cache: Dict[str, Any] = {}
        
        # Initialize disk cache
        self.disk_cache = None
        self.disk_cache_path = os.path.join(self.cache_dir, "translation_cache")
        if self.use_disk:
            self._open_disk_cache()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        # Hash the key for consistency
        hashed_key = self._hash_key(key)
        
        # Check memory cache first
        if self.use_memory and hashed_key in self.memory_cache:
            return self.memory_cache[hashed_key]
        
        # Then check disk cache
        if self.use_disk and self.disk_cache:
            try:
                if hashed_key in self.disk_cache:
                    value = self.disk_cache[hashed_key]
                    # Update memory cache
                    if self.use_memory:
                        self._add_to_memory_cache(hashed_key, value)
                    return value
            except Exception:
                # If disk cache access fails, ignore and return default
                pass
        
        return default
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        # Hash the key for consistency
        hashed_key = self._hash_key(key)
        
        # Update memory cache
        if self.use_memory:
            self._add_to_memory_cache(hashed_key, value)
        
        # Update disk cache
        if self.use_disk and self.disk_cache:
            try:
                self.disk_cache[hashed_key] = value
                self.disk_cache.sync()
            except Exception:
                # If disk cache update fails, ignore
                pass
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        # Hash the key for consistency
        hashed_key = self._hash_key(key)
        
        memory_deleted = False
        disk_deleted = False
        
        # Delete from memory cache
        if self.use_memory and hashed_key in self.memory_cache:
            del self.memory_cache[hashed_key]
            memory_deleted = True
        
        # Delete from disk cache
        if self.use_disk and self.disk_cache:
            try:
                if hashed_key in self.disk_cache:
                    del self.disk_cache[hashed_key]
                    self.disk_cache.sync()
                    disk_deleted = True
            except Exception:
                # If disk cache deletion fails, ignore
                pass
        
        return memory_deleted or disk_deleted
    
    def clear(self) -> None:
        """Clear all cache entries."""
        # Clear memory cache
        if self.use_memory:
            self.memory_cache.clear()
        
        # Clear disk cache
        if self.use_disk and self.disk_cache:
            try:
                self.disk_cache.clear()
                self.disk_cache.sync()
            except Exception:
                # If disk cache clearing fails, ignore
                pass
    
    def close(self) -> None:
        """Close the cache and release resources."""
        # Close disk cache
        if self.use_disk and self.disk_cache:
            try:
                self.disk_cache.close()
                self.disk_cache = None
            except Exception:
                # If disk cache closing fails, ignore
                pass
    
    def _hash_key(self, key: str) -> str:
        """
        Hash a cache key.
        
        Args:
            key: Original key
            
        Returns:
            Hashed key
        """
        return hashlib.md5(key.encode()).hexdigest()
    
    def _add_to_memory_cache(self, hashed_key: str, value: Any) -> None:
        """
        Add an entry to the memory cache, respecting the maximum size.
        
        Args:
            hashed_key: Hashed key
            value: Value to cache
        """
        # Check if we need to evict entries
        if len(self.memory_cache) >= self.max_entries:
            # Simple LRU: remove oldest entry (first key)
            if self.memory_cache:
                oldest_key = next(iter(self.memory_cache))
                del self.memory_cache[oldest_key]
        
        # Add new entry
        self.memory_cache[hashed_key] = value
    
    def _open_disk_cache(self) -> None:
        """Open the disk cache."""
        try:
            self.disk_cache = shelve.open(self.disk_cache_path)
        except Exception as e:
            print(f"Warning: Failed to open disk cache: {e}")
            self.disk_cache = None