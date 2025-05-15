import shelve

class Cache:
    """
    Simple cache implementation with optional persistence
    """
    
    def __init__(self, path=None):
        """
        Initialize cache
        
        Args:
            path: Optional path to shelve file for persistence
        """
        self.in_memory = {}
        self.path = path
        self.shelf = None
        
        if path:
            self.shelf = shelve.open(path)
        
    def get(self, key):
        """
        Get a value from the cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if self.shelf:
            return self.shelf.get(key)
        return self.in_memory.get(key)
        
    def set(self, key, value):
        """
        Set a value in the cache
        
        Args:
            key: Cache key
            value: Value to cache
        """
        if self.shelf:
            self.shelf[key] = value
        else:
            self.in_memory[key] = value
            
    def close(self):
        """Close the cache and any open resources"""
        if self.shelf:
            self.shelf.close()
            self.shelf = None