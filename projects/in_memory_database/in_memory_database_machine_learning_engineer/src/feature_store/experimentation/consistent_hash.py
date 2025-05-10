"""
Consistent hashing for stable experimental group assignment.
"""

import hashlib
import math
from typing import Dict, List, Optional, Set, Tuple, Union, cast

import xxhash
from pydantic import BaseModel, Field, validator


class ConsistentHash(BaseModel):
    """
    Consistent hashing implementation for stable experimental group assignment.
    
    This class implements consistent hashing with virtual nodes to provide
    stable assignments even when the number of buckets changes.
    """

    num_buckets: int = Field(..., description="Number of buckets")
    num_replicas: int = Field(100, description="Number of virtual nodes per bucket")
    hash_seed: int = Field(0, description="Seed for hash function")
    _ring: Dict[int, int] = Field(default_factory=dict, description="Hash ring mapping")
    
    class Config:
        """Pydantic configuration."""
        
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        """Initialize a ConsistentHash instance.
        
        Args:
            **data: Fields to initialize with
        """
        super().__init__(**data)
        self._build_ring()
    
    @validator("num_buckets")
    def validate_num_buckets(cls, v):
        """Validate number of buckets."""
        if v <= 0:
            raise ValueError("Number of buckets must be positive")
        return v
    
    @validator("num_replicas")
    def validate_num_replicas(cls, v):
        """Validate number of replicas."""
        if v <= 0:
            raise ValueError("Number of replicas must be positive")
        return v
    
    def _build_ring(self) -> None:
        """Build the hash ring with virtual nodes."""
        self._ring = {}
        
        for bucket in range(self.num_buckets):
            for replica in range(self.num_replicas):
                # Create a unique key for this replica of this bucket
                key = f"{bucket}:{replica}"
                
                # Hash the key
                hash_val = self._hash(key)
                
                # Add to ring
                self._ring[hash_val] = bucket
    
    def _hash(self, key: str) -> int:
        """Hash a key to an integer.
        
        Args:
            key: Key to hash
            
        Returns:
            Hash value
        """
        # Use xxhash for speed and quality
        return xxhash.xxh64(key, seed=self.hash_seed).intdigest()
    
    def get_bucket(self, key: str) -> int:
        """Get the bucket for a key.
        
        Args:
            key: Key to hash
            
        Returns:
            Bucket index
        """
        # If there's only one bucket, return it directly
        if self.num_buckets == 1:
            return 0
        
        # Hash the key
        hash_val = self._hash(key)
        
        # Find the next bucket in the ring
        for point in sorted(self._ring.keys()):
            if hash_val <= point:
                return self._ring[point]
        
        # If we reached the end of the ring, wrap around
        return self._ring[min(self._ring.keys())]
    
    def get_bucket_normalized(self, key: str) -> float:
        """Get the bucket for a key as a normalized value [0, 1).
        
        This is useful for percentage-based splitting.
        
        Args:
            key: Key to hash
            
        Returns:
            Normalized bucket value in [0, 1)
        """
        bucket = self.get_bucket(key)
        return bucket / self.num_buckets
    
    def get_bucket_distribution(self, keys: List[str]) -> Dict[int, int]:
        """Get the distribution of keys across buckets.
        
        Args:
            keys: List of keys to check
            
        Returns:
            Dictionary mapping bucket index to count
        """
        distribution = {bucket: 0 for bucket in range(self.num_buckets)}
        
        for key in keys:
            bucket = self.get_bucket(key)
            distribution[bucket] += 1
        
        return distribution
    
    def is_in_range(self, key: str, start: float, end: float) -> bool:
        """Check if a key's normalized bucket value is in the given range.
        
        Args:
            key: Key to check
            start: Start of range (inclusive)
            end: End of range (exclusive)
            
        Returns:
            True if the key's bucket is in the range, False otherwise
        """
        if start < 0 or end > 1 or start >= end:
            raise ValueError(f"Invalid range: [{start}, {end})")
        
        value = self.get_bucket_normalized(key)
        return start <= value < end
    
    def update_num_buckets(self, new_num_buckets: int) -> None:
        """Update the number of buckets.
        
        This will rebuild the hash ring, but assignments will be stable
        for most keys.
        
        Args:
            new_num_buckets: New number of buckets
            
        Raises:
            ValueError: If new_num_buckets is not positive
        """
        if new_num_buckets <= 0:
            raise ValueError("Number of buckets must be positive")
        
        self.num_buckets = new_num_buckets
        self._build_ring()
    
    def update_hash_seed(self, new_seed: int) -> None:
        """Update the hash seed.
        
        This will rebuild the hash ring and change all assignments.
        
        Args:
            new_seed: New hash seed
        """
        self.hash_seed = new_seed
        self._build_ring()
    
    def setup_percentage_based(
        self, 
        percentages: List[float],
        seed: Optional[int] = None
    ) -> List[Tuple[float, float]]:
        """Set up for percentage-based assignment.
        
        Args:
            percentages: List of percentages for each group (must sum to 1)
            seed: Optional new hash seed
            
        Returns:
            List of (start, end) ranges for each group
            
        Raises:
            ValueError: If percentages don't sum to 1
        """
        # Validate percentages
        if not math.isclose(sum(percentages), 1.0, abs_tol=1e-6):
            raise ValueError(f"Percentages must sum to 1, got {sum(percentages)}")
        
        # Update seed if provided
        if seed is not None:
            self.update_hash_seed(seed)
        
        # Calculate ranges
        ranges = []
        start = 0.0
        for pct in percentages:
            end = start + pct
            ranges.append((start, end))
            start = end
        
        return ranges
    
    def get_group_for_ranges(
        self, 
        key: str, 
        ranges: List[Tuple[float, float]]
    ) -> int:
        """Get the group for a key based on ranges.
        
        Args:
            key: Key to check
            ranges: List of (start, end) ranges for each group
            
        Returns:
            Group index
        """
        value = self.get_bucket_normalized(key)
        
        for i, (start, end) in enumerate(ranges):
            if start <= value < end:
                return i
        
        # If we reach here, the key falls outside all ranges
        # This shouldn't happen if ranges cover [0, 1), but handle it anyway
        return 0