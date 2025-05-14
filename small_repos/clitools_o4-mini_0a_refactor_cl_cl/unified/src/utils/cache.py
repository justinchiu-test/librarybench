"""
Caching utilities for CLI applications.

This module provides caching functionality for improving performance of repeated operations.
"""

import os
import time
import shelve
import functools
import json
import hashlib
from typing import Dict, Any, Optional, Union, Callable, TypeVar, cast

# Type variables for better type hints
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])


class Cache:
    """
    Simple cache implementation with optional disk persistence.
    """
    
    def __init__(self, cache_file: Optional[str] = None):
        """
        Initialize the cache.
        
        Args:
            cache_file (str, optional): Path to the cache file for persistence.
        """
        self.memory_cache: Dict[str, Any] = {}
        self.cache_file = cache_file
        self.shelf = None
        
        # Open disk cache if specified
        if cache_file:
            self._open_shelf()
    
    def _open_shelf(self) -> None:
        """Open the shelf file for disk caching."""
        try:
            # Ensure directory exists
            if self.cache_file:
                cache_dir = os.path.dirname(os.path.abspath(self.cache_file))
                os.makedirs(cache_dir, exist_ok=True)
                
                self.shelf = shelve.open(self.cache_file)
        except Exception:
            self.shelf = None
    
    def get(self, key: str) -> Any:
        """
        Get a value from the cache.
        
        Args:
            key (str): Cache key.
            
        Returns:
            The cached value or None if not found.
        """
        # Try memory cache first
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # Then try disk cache
        if self.shelf is not None:
            try:
                if key in self.shelf:
                    value = self.shelf[key]
                    # Cache in memory for faster access
                    self.memory_cache[key] = value
                    return value
            except Exception:
                pass
        
        return None
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache.
        
        Args:
            key (str): Cache key.
            value: Value to cache.
        """
        # Set in memory cache
        self.memory_cache[key] = value
        
        # Set in disk cache if available
        if self.shelf is not None:
            try:
                self.shelf[key] = value
                self.shelf.sync()
            except Exception:
                pass
    
    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.
        
        Args:
            key (str): Cache key.
        """
        # Remove from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # Remove from disk cache if available
        if self.shelf is not None:
            try:
                if key in self.shelf:
                    del self.shelf[key]
                    self.shelf.sync()
            except Exception:
                pass
    
    def clear(self) -> None:
        """Clear all cached values."""
        # Clear memory cache
        self.memory_cache.clear()
        
        # Clear disk cache if available
        if self.shelf is not None:
            try:
                self.shelf.clear()
                self.shelf.sync()
            except Exception:
                pass
    
    def close(self) -> None:
        """Close the disk cache."""
        if self.shelf is not None:
            try:
                self.shelf.close()
                self.shelf = None
            except Exception:
                pass
    
    def __del__(self) -> None:
        """Ensure the disk cache is closed on object deletion."""
        self.close()


def memoize(func: F) -> F:
    """
    Decorator to memoize a function's results.
    
    Args:
        func (Callable): Function to memoize.
        
    Returns:
        Callable: Memoized function.
    """
    cache: Dict[str, Any] = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from the function arguments
        key_parts = [repr(arg) for arg in args]
        key_parts.extend(f"{k}={repr(v)}" for k, v in sorted(kwargs.items()))
        key = ":".join(key_parts)
        
        # Return cached result if available
        if key in cache:
            return cache[key]
        
        # Compute and cache result
        result = func(*args, **kwargs)
        cache[key] = result
        return result
    
    # Add function to clear the cache
    def clear_cache():
        cache.clear()
    
    wrapper.clear_cache = clear_cache  # type: ignore
    
    return cast(F, wrapper)


def timed_cache(max_age: float = 60.0) -> Callable[[F], F]:
    """
    Decorator for caching function results with expiration.
    
    Args:
        max_age (float): Maximum age of cached values in seconds.
        
    Returns:
        Callable: Decorator function.
    """
    def decorator(func: F) -> F:
        cache: Dict[str, Dict[str, Any]] = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from the function arguments
            key_parts = [repr(arg) for arg in args]
            key_parts.extend(f"{k}={repr(v)}" for k, v in sorted(kwargs.items()))
            key = ":".join(key_parts)
            
            # Check if we have a cached value that hasn't expired
            now = time.time()
            if key in cache and now - cache[key]['timestamp'] < max_age:
                return cache[key]['value']
            
            # Compute and cache result with timestamp
            result = func(*args, **kwargs)
            cache[key] = {
                'value': result,
                'timestamp': now
            }
            return result
        
        # Add function to clear the cache
        def clear_cache():
            cache.clear()
        
        wrapper.clear_cache = clear_cache  # type: ignore
        
        return cast(F, wrapper)
    
    return decorator