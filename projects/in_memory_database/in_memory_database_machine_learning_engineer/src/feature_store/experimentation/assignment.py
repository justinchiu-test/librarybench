"""
Assignment strategies for experiment groups.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union, cast

from pydantic import BaseModel, Field, validator

from feature_store.experimentation.consistent_hash import ConsistentHash


class AssignmentType(Enum):
    """Types of assignment strategies."""
    
    PERCENTAGE = "percentage"  # Assign by percentage
    HASH_MOD = "hash_mod"      # Assign by hash modulo
    KEY_PREFIX = "key_prefix"  # Assign by key prefix
    LIST_BASED = "list_based"  # Assign from explicit lists
    RANDOM = "random"          # Completely random assignment


class AssignmentStrategy(ABC, BaseModel):
    """
    Abstract base class for assignment strategies.
    
    All assignment strategies must inherit from this class and implement
    the required methods.
    """

    assignment_type: AssignmentType = Field(..., description="Type of assignment strategy")
    groups: List[str] = Field(..., description="List of group names")
    salt: str = Field("", description="Salt to add when hashing keys")
    
    class Config:
        """Pydantic configuration."""
        
        arbitrary_types_allowed = True
    
    @abstractmethod
    def assign(self, key: str) -> str:
        """Assign a key to a group.
        
        Args:
            key: Key to assign
            
        Returns:
            Group name
        """
        pass
    
    @abstractmethod
    def is_in_group(self, key: str, group: str) -> bool:
        """Check if a key is in a specific group.
        
        Args:
            key: Key to check
            group: Group name to check
            
        Returns:
            True if the key is in the group, False otherwise
        """
        pass
    
    @validator("groups")
    def validate_groups(cls, v):
        """Validate groups."""
        if not v:
            raise ValueError("Groups list cannot be empty")
        return v
    
    def _get_salted_key(self, key: str) -> str:
        """Get a salted key.
        
        Args:
            key: Original key
            
        Returns:
            Salted key
        """
        if not self.salt:
            return key
        return f"{self.salt}:{key}"


class PercentageAssignment(AssignmentStrategy):
    """
    Percentage-based assignment strategy.
    
    Assigns keys to groups based on percentage weights using consistent hashing.
    """

    assignment_type: AssignmentType = Field(AssignmentType.PERCENTAGE, const=True)
    weights: List[float] = Field(..., description="Weights for each group (must sum to 1)")
    hash_seed: int = Field(0, description="Seed for hash function")
    _hash: ConsistentHash = Field(None, description="Consistent hash implementation")
    _ranges: List[Tuple[float, float]] = Field(default_factory=list, description="Assignment ranges")
    
    def __init__(self, **data):
        """Initialize a PercentageAssignment instance.
        
        Args:
            **data: Fields to initialize with
        """
        super().__init__(**data)
        self._init_hash()
    
    @validator("weights")
    def validate_weights(cls, v, values):
        """Validate weights."""
        if "groups" in values and len(v) != len(values["groups"]):
            raise ValueError(f"Number of weights ({len(v)}) must match number of groups ({len(values['groups'])})")
        
        if not all(w >= 0 for w in v):
            raise ValueError("Weights must be non-negative")
        
        if abs(sum(v) - 1.0) > 1e-6:
            raise ValueError(f"Weights must sum to 1, got {sum(v)}")
        
        return v
    
    def _init_hash(self) -> None:
        """Initialize the consistent hash."""
        # Use 1000 buckets for fine-grained assignment
        self._hash = ConsistentHash(
            num_buckets=1000,
            hash_seed=self.hash_seed
        )
        
        # Set up percentage-based assignment
        self._ranges = self._hash.setup_percentage_based(self.weights)
    
    def assign(self, key: str) -> str:
        """Assign a key to a group.
        
        Args:
            key: Key to assign
            
        Returns:
            Group name
        """
        # Get salted key
        salted_key = self._get_salted_key(key)
        
        # Get group index
        group_idx = self._hash.get_group_for_ranges(salted_key, self._ranges)
        
        # Return group name
        return self.groups[group_idx]
    
    def is_in_group(self, key: str, group: str) -> bool:
        """Check if a key is in a specific group.
        
        Args:
            key: Key to check
            group: Group name to check
            
        Returns:
            True if the key is in the group, False otherwise
        """
        if group not in self.groups:
            raise ValueError(f"Unknown group: {group}")
        
        return self.assign(key) == group
    
    def update_weights(self, new_weights: List[float]) -> None:
        """Update the weights for groups.
        
        Args:
            new_weights: New weights for each group
            
        Raises:
            ValueError: If invalid weights
        """
        if len(new_weights) != len(self.groups):
            raise ValueError(f"Number of weights ({len(new_weights)}) must match number of groups ({len(self.groups)})")
        
        if not all(w >= 0 for w in new_weights):
            raise ValueError("Weights must be non-negative")
        
        if abs(sum(new_weights) - 1.0) > 1e-6:
            raise ValueError(f"Weights must sum to 1, got {sum(new_weights)}")
        
        self.weights = new_weights
        self._ranges = self._hash.setup_percentage_based(self.weights)


class HashModAssignment(AssignmentStrategy):
    """
    Hash modulo assignment strategy.
    
    Assigns keys to groups based on hash modulo.
    """

    assignment_type: AssignmentType = Field(AssignmentType.HASH_MOD, const=True)
    hash_seed: int = Field(0, description="Seed for hash function")
    _hash: ConsistentHash = Field(None, description="Consistent hash implementation")
    
    def __init__(self, **data):
        """Initialize a HashModAssignment instance.
        
        Args:
            **data: Fields to initialize with
        """
        super().__init__(**data)
        self._init_hash()
    
    def _init_hash(self) -> None:
        """Initialize the consistent hash."""
        # Use number of groups as number of buckets
        self._hash = ConsistentHash(
            num_buckets=len(self.groups),
            hash_seed=self.hash_seed
        )
    
    def assign(self, key: str) -> str:
        """Assign a key to a group.
        
        Args:
            key: Key to assign
            
        Returns:
            Group name
        """
        # Get salted key
        salted_key = self._get_salted_key(key)
        
        # Get bucket (group index)
        group_idx = self._hash.get_bucket(salted_key)
        
        # Return group name
        return self.groups[group_idx]
    
    def is_in_group(self, key: str, group: str) -> bool:
        """Check if a key is in a specific group.
        
        Args:
            key: Key to check
            group: Group name to check
            
        Returns:
            True if the key is in the group, False otherwise
        """
        if group not in self.groups:
            raise ValueError(f"Unknown group: {group}")
        
        return self.assign(key) == group


class ListBasedAssignment(AssignmentStrategy):
    """
    List-based assignment strategy.
    
    Assigns keys to groups based on explicit lists of keys.
    """

    assignment_type: AssignmentType = Field(AssignmentType.LIST_BASED, const=True)
    key_lists: Dict[str, Set[str]] = Field(..., description="Map of group name to set of keys")
    default_group: Optional[str] = Field(None, description="Default group for unknown keys")
    
    @validator("key_lists")
    def validate_key_lists(cls, v, values):
        """Validate key lists."""
        if "groups" in values:
            if set(v.keys()) != set(values["groups"]):
                raise ValueError("Key lists must have an entry for each group")
                
        # Check for overlapping keys
        all_keys = set()
        overlapping = set()
        for keys in v.values():
            overlapping.update(all_keys.intersection(keys))
            all_keys.update(keys)
        
        if overlapping:
            # Limit to showing first 5 overlapping keys in the error
            display_keys = list(overlapping)[:5]
            overflow = len(overlapping) - 5
            overflow_msg = f" and {overflow} more" if overflow > 0 else ""
            raise ValueError(f"Found overlapping keys in multiple groups: {display_keys}{overflow_msg}")
            
        return v
    
    def assign(self, key: str) -> str:
        """Assign a key to a group.
        
        Args:
            key: Key to assign
            
        Returns:
            Group name
            
        Raises:
            ValueError: If key is not in any group and no default group is set
        """
        # Check each group for the key
        for group, keys in self.key_lists.items():
            if key in keys:
                return group
        
        # Key not found in any group, use default if available
        if self.default_group is not None:
            return self.default_group
        
        raise ValueError(f"Key not found in any group: {key}")
    
    def is_in_group(self, key: str, group: str) -> bool:
        """Check if a key is in a specific group.
        
        Args:
            key: Key to check
            group: Group name to check
            
        Returns:
            True if the key is in the group, False otherwise
        """
        if group not in self.groups:
            raise ValueError(f"Unknown group: {group}")
        
        # Direct check in the key list
        return key in self.key_lists[group]
    
    def add_key_to_group(self, key: str, group: str) -> None:
        """Add a key to a group.
        
        Args:
            key: Key to add
            group: Group name
            
        Raises:
            ValueError: If group is unknown
            ValueError: If key is already in another group
        """
        if group not in self.groups:
            raise ValueError(f"Unknown group: {group}")
        
        # Check if key is already in another group
        for other_group, keys in self.key_lists.items():
            if other_group != group and key in keys:
                raise ValueError(f"Key already in group {other_group}")
        
        # Add to group
        self.key_lists[group].add(key)
    
    def remove_key_from_group(self, key: str, group: str) -> bool:
        """Remove a key from a group.
        
        Args:
            key: Key to remove
            group: Group name
            
        Returns:
            True if the key was removed, False if it wasn't in the group
            
        Raises:
            ValueError: If group is unknown
        """
        if group not in self.groups:
            raise ValueError(f"Unknown group: {group}")
        
        # Check if key is in the group
        if key not in self.key_lists[group]:
            return False
        
        # Remove from group
        self.key_lists[group].remove(key)
        return True