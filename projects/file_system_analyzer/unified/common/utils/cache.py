"""Caching utilities for file system analysis.

This module provides caching mechanisms to improve performance of repeated
file system analysis operations.
"""

import os
import json
import pickle
import hashlib
import logging
import threading
import tempfile
from typing import Dict, List, Optional, Any, Union, TypeVar, Generic, Callable
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


T = TypeVar('T')  # Type variable for cached values


class CacheEntry(BaseModel, Generic[T]):
    """Cache entry with metadata."""
    
    value: T
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def age(self) -> timedelta:
        """Get the age of the cache entry."""
        return datetime.now() - self.created_at
    
    @property
    def is_expired(self) -> bool:
        """Check if the cache entry is expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class MemoryCache(Generic[T]):
    """In-memory cache for analysis results."""
    
    def __init__(
        self, 
        ttl_seconds: Optional[int] = None, 
        max_size: int = 1000
    ):
        """
        Initialize memory cache.
        
        Args:
            ttl_seconds: Time-to-live in seconds, or None for no expiration
            max_size: Maximum number of entries in the cache
        """
        self.cache: Dict[str, CacheEntry[T]] = {}
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.lock = threading.RLock()
        
    def get(self, key: str) -> Optional[T]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value, or None if not found or expired
        """
        with self.lock:
            entry = self.cache.get(key)
            
            if entry is None:
                return None
                
            if entry.is_expired:
                # Remove expired entry
                del self.cache[key]
                return None
                
            return entry.value
            
    def set(
        self, 
        key: str, 
        value: T, 
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override for this entry
            metadata: Optional metadata for the cache entry
        """
        with self.lock:
            # Enforce max cache size
            if len(self.cache) >= self.max_size and key not in self.cache:
                # Evict the oldest entry
                oldest_key = min(
                    self.cache.items(), 
                    key=lambda item: item[1].created_at
                )[0]
                del self.cache[oldest_key]
            
            # Calculate expiration time
            expires_at = None
            if ttl_seconds is not None:
                expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            elif self.ttl_seconds is not None:
                expires_at = datetime.now() + timedelta(seconds=self.ttl_seconds)
            
            # Create cache entry
            entry = CacheEntry(
                value=value,
                created_at=datetime.now(),
                expires_at=expires_at,
                metadata=metadata or {}
            )
            
            self.cache[key] = entry
    
    def delete(self, key: str) -> bool:
        """
        Delete an entry from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if the key was found and deleted, False otherwise
        """
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self.lock:
            self.cache.clear()
    
    def get_all_keys(self) -> List[str]:
        """
        Get all keys in the cache.
        
        Returns:
            List of all cache keys
        """
        with self.lock:
            return list(self.cache.keys())
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            expired_count = sum(1 for entry in self.cache.values() if entry.is_expired)
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "ttl_seconds": self.ttl_seconds,
                "expired_count": expired_count,
                "oldest_entry_age": min(
                    (entry.age.total_seconds() for entry in self.cache.values()),
                    default=0
                ),
                "newest_entry_age": max(
                    (entry.age.total_seconds() for entry in self.cache.values()),
                    default=0
                )
            }


class DiskCache(Generic[T]):
    """Disk-based cache for analysis results."""
    
    def __init__(
        self, 
        cache_dir: Optional[Union[str, Path]] = None,
        ttl_seconds: Optional[int] = None,
        max_size: int = 1000,
        max_bytes: Optional[int] = None
    ):
        """
        Initialize disk cache.
        
        Args:
            cache_dir: Directory to store cache files, or None for default temp directory
            ttl_seconds: Time-to-live in seconds, or None for no expiration
            max_size: Maximum number of entries in the cache
            max_bytes: Maximum size of the cache in bytes, or None for no limit
        """
        if cache_dir is None:
            self.cache_dir = Path(tempfile.gettempdir()) / "file_system_analyzer_cache"
        else:
            self.cache_dir = Path(cache_dir)
            
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self.max_bytes = max_bytes
        self.index_file = self.cache_dir / "index.json"
        self.lock = threading.RLock()
        
        # Initialize cache directory and index
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize cache directory and index."""
        try:
            # Create cache directory if it doesn't exist
            if not self.cache_dir.exists():
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                
            # Create or load index
            if not self.index_file.exists():
                self._save_index({})
        except Exception as e:
            logger.error(f"Error initializing disk cache: {e}")
    
    def _get_cache_path(self, key: str) -> Path:
        """
        Get the path to a cache file.
        
        Args:
            key: Cache key
            
        Returns:
            Path to the cache file
        """
        # Hash the key to create a valid filename
        hashed_key = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{hashed_key}.cache"
    
    def _load_index(self) -> Dict[str, Dict[str, Any]]:
        """
        Load the cache index.
        
        Returns:
            Dictionary mapping cache keys to cache entry metadata
        """
        if not self.index_file.exists():
            return {}
            
        try:
            with open(self.index_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading cache index: {e}")
            return {}
    
    def _save_index(self, index: Dict[str, Dict[str, Any]]) -> None:
        """
        Save the cache index.
        
        Args:
            index: Dictionary mapping cache keys to cache entry metadata
        """
        try:
            with open(self.index_file, 'w') as f:
                json.dump(index, f, default=str)
        except Exception as e:
            logger.error(f"Error saving cache index: {e}")
    
    def _is_entry_expired(self, metadata: Dict[str, Any]) -> bool:
        """
        Check if a cache entry is expired.
        
        Args:
            metadata: Cache entry metadata
            
        Returns:
            True if the cache entry is expired, False otherwise
        """
        if "expires_at" not in metadata:
            return False
            
        try:
            expires_at = datetime.fromisoformat(metadata["expires_at"])
            return datetime.now() > expires_at
        except (ValueError, TypeError):
            # If we can't parse the expiration time, assume not expired
            return False
    
    def get(self, key: str) -> Optional[T]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value, or None if not found or expired
        """
        with self.lock:
            # Load index
            index = self._load_index()
            
            # Check if key exists in index
            if key not in index:
                return None
            
            # Check if entry is expired
            if self._is_entry_expired(index[key]):
                # Remove expired entry
                self.delete(key)
                return None
            
            # Get cache file path
            cache_path = self._get_cache_path(key)
            
            # Check if cache file exists
            if not cache_path.exists():
                # Remove from index if file is missing
                del index[key]
                self._save_index(index)
                return None
            
            # Load cache file
            try:
                with open(cache_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.error(f"Error loading cache file for key {key}: {e}")
                
                # Remove corrupted entry
                self.delete(key)
                return None
    
    def set(
        self, 
        key: str, 
        value: T, 
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Optional TTL override for this entry
            metadata: Optional metadata for the cache entry
        """
        with self.lock:
            # Load index
            index = self._load_index()
            
            # Calculate expiration time
            expires_at = None
            if ttl_seconds is not None:
                expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
            elif self.ttl_seconds is not None:
                expires_at = datetime.now() + timedelta(seconds=self.ttl_seconds)
            
            # Create entry metadata
            entry_metadata = {
                "created_at": datetime.now().isoformat(),
                "expires_at": expires_at.isoformat() if expires_at else None,
                **(metadata or {})
            }
            
            # Save cache file
            cache_path = self._get_cache_path(key)
            try:
                with open(cache_path, 'wb') as f:
                    pickle.dump(value, f)
            except Exception as e:
                logger.error(f"Error saving cache file for key {key}: {e}")
                return
            
            # Update index
            index[key] = entry_metadata
            self._save_index(index)
            
            # Enforce max cache size
            self._enforce_limits()
    
    def delete(self, key: str) -> bool:
        """
        Delete an entry from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if the key was found and deleted, False otherwise
        """
        with self.lock:
            # Load index
            index = self._load_index()
            
            # Check if key exists in index
            if key not in index:
                return False
            
            # Remove from index
            del index[key]
            self._save_index(index)
            
            # Remove cache file
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                try:
                    cache_path.unlink()
                except Exception as e:
                    logger.error(f"Error deleting cache file for key {key}: {e}")
            
            return True
    
    def clear(self) -> None:
        """Clear all entries from the cache."""
        with self.lock:
            # Load index
            index = self._load_index()
            
            # Delete all cache files
            for key in list(index.keys()):
                cache_path = self._get_cache_path(key)
                if cache_path.exists():
                    try:
                        cache_path.unlink()
                    except Exception as e:
                        logger.error(f"Error deleting cache file for key {key}: {e}")
            
            # Clear index
            self._save_index({})
    
    def _enforce_limits(self) -> None:
        """Enforce cache size limits."""
        with self.lock:
            # Load index
            index = self._load_index()
            
            # Nothing to do if within limits
            if len(index) <= self.max_size and (
                self.max_bytes is None or self._get_total_size() <= self.max_bytes
            ):
                return
            
            # Sort entries by creation time (oldest first)
            sorted_entries = sorted(
                index.items(),
                key=lambda item: datetime.fromisoformat(item[1]["created_at"])
            )
            
            # Remove entries until within limits
            while sorted_entries and (
                len(sorted_entries) > self.max_size or
                (self.max_bytes is not None and self._get_total_size() > self.max_bytes)
            ):
                key, _ = sorted_entries.pop(0)
                self.delete(key)
    
    def _get_total_size(self) -> int:
        """
        Get the total size of the cache in bytes.
        
        Returns:
            Total size of all cache files in bytes
        """
        total_size = 0
        for file_path in self.cache_dir.glob("*.cache"):
            try:
                total_size += file_path.stat().st_size
            except Exception:
                pass
        return total_size
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            index = self._load_index()
            
            expired_count = sum(
                1 for metadata in index.values() 
                if self._is_entry_expired(metadata)
            )
            
            return {
                "size": len(index),
                "max_size": self.max_size,
                "ttl_seconds": self.ttl_seconds,
                "max_bytes": self.max_bytes,
                "current_bytes": self._get_total_size(),
                "expired_count": expired_count,
                "cache_dir": str(self.cache_dir)
            }


def cache_result(
    ttl_seconds: Optional[int] = None,
    key_fn: Optional[Callable[..., str]] = None,
    cache: Optional[Union[MemoryCache, DiskCache]] = None
):
    """
    Decorator to cache function results.
    
    Args:
        ttl_seconds: Time-to-live in seconds, or None for no expiration
        key_fn: Function to generate cache key from function arguments
        cache: Cache instance to use, or None to create a new MemoryCache
        
    Returns:
        Decorated function
    """
    # Create default cache if none provided
    if cache is None:
        cache = MemoryCache(ttl_seconds=ttl_seconds)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_fn is not None:
                key = key_fn(*args, **kwargs)
            else:
                # Default key generation based on function name and arguments
                key_parts = [func.__name__]
                
                # Add positional arguments
                for arg in args:
                    key_parts.append(str(arg))
                
                # Add keyword arguments (sorted by key)
                for k, v in sorted(kwargs.items()):
                    key_parts.append(f"{k}={v}")
                
                key = ":".join(key_parts)
            
            # Try to get from cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(key, result, ttl_seconds=ttl_seconds)
            
            return result
        
        return wrapper
    
    return decorator