"""Caching utilities shared across implementations."""

import time
import functools
import hashlib
import inspect
import json
from typing import Any, Callable, Dict, Optional, Tuple, Union, TypeVar, cast

T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])


class Cache:
    """Simple in-memory cache with expiration."""
    
    def __init__(self, max_size: int = 1000, expiration_seconds: Optional[int] = None):
        """
        Initialize the cache.
        
        Args:
            max_size: Maximum number of items in the cache
            expiration_seconds: Time in seconds after which items expire (None for no expiration)
        """
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._max_size = max_size
        self._expiration_seconds = expiration_seconds
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value or None if not found or expired
        """
        if key not in self._cache:
            return None
        
        value, timestamp = self._cache[key]
        
        # Check if expired
        if self._expiration_seconds is not None:
            if time.time() - timestamp > self._expiration_seconds:
                # Remove expired item
                del self._cache[key]
                return None
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
        """
        # Ensure we don't exceed max size
        if len(self._cache) >= self._max_size and key not in self._cache:
            # Remove oldest item (simplistic approach)
            oldest_key = min(self._cache.items(), key=lambda x: x[1][1])[0]
            del self._cache[oldest_key]
        
        # Store with current timestamp
        self._cache[key] = (value, time.time())
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: The cache key
            
        Returns:
            True if the key was found and deleted, False otherwise
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
    
    def size(self) -> int:
        """
        Get the current size of the cache.
        
        Returns:
            Number of items in the cache
        """
        return len(self._cache)
    
    def clean_expired(self) -> int:
        """
        Remove all expired entries from the cache.
        
        Returns:
            Number of expired entries removed
        """
        if self._expiration_seconds is None:
            return 0
        
        # Find expired keys
        now = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if now - timestamp > self._expiration_seconds
        ]
        
        # Delete expired keys
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)


def memoize(func: F) -> F:
    """
    Decorator to memoize a function's return value.
    
    Args:
        func: The function to memoize
        
    Returns:
        Memoized function
    """
    cache: Dict[str, Any] = {}
    
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Create a cache key from the function arguments
        key = _create_cache_key(func, args, kwargs)
        
        # Check if result is in cache
        if key in cache:
            return cache[key]
        
        # Call the function and cache the result
        result = func(*args, **kwargs)
        cache[key] = result
        
        return result
    
    # Add cache management functions
    wrapper.cache = cache  # type: ignore
    wrapper.cache_clear = cache.clear  # type: ignore
    wrapper.cache_size = lambda: len(cache)  # type: ignore
    
    return cast(F, wrapper)


def memoize_with_expiry(expiration_seconds: int) -> Callable[[F], F]:
    """
    Create a decorator to memoize a function's return value with expiration.
    
    Args:
        expiration_seconds: Time in seconds after which cached items expire
        
    Returns:
        Decorator function
    """
    def decorator(func: F) -> F:
        # Cache stores tuples of (result, timestamp)
        cache: Dict[str, Tuple[Any, float]] = {}
        
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create a cache key from the function arguments
            key = _create_cache_key(func, args, kwargs)
            
            # Check if result is in cache and not expired
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < expiration_seconds:
                    return result
            
            # Call the function and cache the result with timestamp
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())
            
            return result
        
        # Add cache management functions
        wrapper.cache = cache  # type: ignore
        wrapper.cache_clear = cache.clear  # type: ignore
        wrapper.cache_size = lambda: len(cache)  # type: ignore
        
        # Add function to clean expired entries
        def clean_expired() -> int:
            now = time.time()
            expired_keys = [
                key for key, (_, timestamp) in cache.items()
                if now - timestamp >= expiration_seconds
            ]
            for key in expired_keys:
                del cache[key]
            return len(expired_keys)
        
        wrapper.clean_expired = clean_expired  # type: ignore
        
        return cast(F, wrapper)
    
    return decorator


def _create_cache_key(func: Callable, args: Tuple, kwargs: Dict[str, Any]) -> str:
    """
    Create a cache key for a function call.
    
    Args:
        func: The function
        args: Positional arguments
        kwargs: Keyword arguments
        
    Returns:
        Cache key string
    """
    # Get function signature
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    
    # Create a JSON-serializable representation
    key_dict = {
        "func": f"{func.__module__}.{func.__qualname__}",
        "args": _make_hashable(bound_args.arguments),
    }
    
    # Convert to JSON string and hash for shorter key
    key_json = json.dumps(key_dict, sort_keys=True)
    key_hash = hashlib.md5(key_json.encode()).hexdigest()
    
    return key_hash


def _make_hashable(obj: Any) -> Any:
    """
    Convert an object to a hashable form for caching.
    
    Args:
        obj: The object to make hashable
        
    Returns:
        Hashable representation of the object
    """
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, (list, tuple)):
        return tuple(_make_hashable(x) for x in obj)
    elif isinstance(obj, dict):
        return tuple(
            (k, _make_hashable(v)) for k, v in sorted(obj.items())
        )
    elif hasattr(obj, "__dict__"):
        # For objects with a __dict__, use the dict representation
        return _make_hashable(obj.__dict__)
    else:
        # For other objects, use string representation
        return str(obj)