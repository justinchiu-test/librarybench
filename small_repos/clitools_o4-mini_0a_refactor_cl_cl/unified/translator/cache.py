"""Cache module for translator tools."""

class Cache:
    """Simple cache implementation with optional disk persistence."""
    
    def __init__(self, cache_file=None):
        """Initialize the cache."""
        self.memory_cache = {}
        self.cache_file = cache_file
        self.shelf = None
        
        # Open disk cache if specified
        if cache_file:
            self._open_shelf()
    
    def _open_shelf(self):
        """Open the shelf file for disk caching."""
        import shelve
        import os
        
        try:
            # Ensure directory exists
            if self.cache_file:
                cache_dir = os.path.dirname(os.path.abspath(self.cache_file))
                os.makedirs(cache_dir, exist_ok=True)
                
                self.shelf = shelve.open(self.cache_file)
        except Exception:
            self.shelf = None
    
    def get(self, key):
        """Get a value from the cache."""
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
    
    def set(self, key, value):
        """Set a value in the cache."""
        # Set in memory cache
        self.memory_cache[key] = value
        
        # Set in disk cache if available
        if self.shelf is not None:
            try:
                self.shelf[key] = value
                self.shelf.sync()
            except Exception:
                pass
    
    def close(self):
        """Close the disk cache."""
        if self.shelf is not None:
            try:
                self.shelf.close()
                self.shelf = None
            except Exception:
                pass