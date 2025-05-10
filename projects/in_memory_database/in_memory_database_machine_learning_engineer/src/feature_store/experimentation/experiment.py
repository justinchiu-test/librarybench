"""
Experimentation framework with A/B testing support.
"""

import time
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union, cast, Any

from pydantic import BaseModel, Field, validator

from feature_store.experimentation.assignment import (
    AssignmentStrategy, AssignmentType, HashModAssignment, ListBasedAssignment, PercentageAssignment
)


class ExperimentStatus(Enum):
    """Status of an experiment."""
    
    DRAFT = "draft"  # Experiment is being drafted, not yet ready for use
    ACTIVE = "active"  # Experiment is active and assigning units
    PAUSED = "paused"  # Experiment is paused, not assigning new units
    COMPLETED = "completed"  # Experiment is completed, no longer assigning units
    ARCHIVED = "archived"  # Experiment is archived, kept for reference only


class Experiment(BaseModel):
    """
    Experiment for A/B testing with randomized but consistent record selection.
    
    This class manages an experiment with multiple treatment groups and provides
    consistent assignment of keys to groups.
    """

    name: str = Field(..., description="Unique name of the experiment")
    description: str = Field("", description="Description of the experiment")
    groups: List[str] = Field(..., description="List of group names")
    assignment_strategy: AssignmentStrategy = Field(..., description="Strategy for assigning keys to groups")
    status: ExperimentStatus = Field(ExperimentStatus.DRAFT, description="Status of the experiment")
    created_at: float = Field(default_factory=time.time, description="Unix timestamp when experiment was created")
    updated_at: float = Field(default_factory=time.time, description="Unix timestamp when experiment was last updated")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic configuration."""
        
        arbitrary_types_allowed = True
    
    @validator("groups")
    def validate_groups(cls, v):
        """Validate groups."""
        if not v:
            raise ValueError("Groups cannot be empty")
        
        if len(v) != len(set(v)):
            raise ValueError("Groups must be unique")
        
        return v
    
    @classmethod
    def create_percentage_based(
        cls,
        name: str,
        groups: List[str],
        weights: List[float],
        salt: str = "",
        hash_seed: int = 0,
        description: str = "",
        metadata: Optional[Dict[str, str]] = None
    ) -> "Experiment":
        """Create a percentage-based experiment.
        
        Args:
            name: Experiment name
            groups: List of group names
            weights: Weights for each group (must sum to 1)
            salt: Optional salt for hashing
            hash_seed: Seed for hash function
            description: Experiment description
            metadata: Additional metadata
            
        Returns:
            New Experiment instance
        """
        assignment = PercentageAssignment(
            groups=groups,
            weights=weights,
            salt=salt,
            hash_seed=hash_seed
        )
        
        return cls(
            name=name,
            description=description,
            groups=groups,
            assignment_strategy=assignment,
            metadata=metadata or {}
        )
    
    @classmethod
    def create_hash_based(
        cls,
        name: str,
        groups: List[str],
        salt: str = "",
        hash_seed: int = 0,
        description: str = "",
        metadata: Optional[Dict[str, str]] = None
    ) -> "Experiment":
        """Create a hash-based experiment.
        
        Args:
            name: Experiment name
            groups: List of group names
            salt: Optional salt for hashing
            hash_seed: Seed for hash function
            description: Experiment description
            metadata: Additional metadata
            
        Returns:
            New Experiment instance
        """
        assignment = HashModAssignment(
            groups=groups,
            salt=salt,
            hash_seed=hash_seed
        )
        
        return cls(
            name=name,
            description=description,
            groups=groups,
            assignment_strategy=assignment,
            metadata=metadata or {}
        )
    
    @classmethod
    def create_list_based(
        cls,
        name: str,
        key_lists: Dict[str, Set[str]],
        default_group: Optional[str] = None,
        description: str = "",
        metadata: Optional[Dict[str, str]] = None
    ) -> "Experiment":
        """Create a list-based experiment.
        
        Args:
            name: Experiment name
            key_lists: Map of group name to set of keys
            default_group: Optional default group for unknown keys
            description: Experiment description
            metadata: Additional metadata
            
        Returns:
            New Experiment instance
        """
        groups = list(key_lists.keys())
        
        assignment = ListBasedAssignment(
            groups=groups,
            key_lists=key_lists,
            default_group=default_group,
            salt=""  # No salt needed for list-based assignment
        )
        
        return cls(
            name=name,
            description=description,
            groups=groups,
            assignment_strategy=assignment,
            metadata=metadata or {}
        )
    
    def get_group(self, key: str) -> str:
        """Get the group for a key.
        
        Args:
            key: Key to check
            
        Returns:
            Group name
            
        Raises:
            RuntimeError: If experiment is not active
        """
        if self.status != ExperimentStatus.ACTIVE:
            raise RuntimeError(f"Experiment {self.name} is not active (status: {self.status.value})")
        
        return self.assignment_strategy.assign(key)
    
    def is_in_group(self, key: str, group: str) -> bool:
        """Check if a key is in a specific group.
        
        Args:
            key: Key to check
            group: Group name to check
            
        Returns:
            True if the key is in the group, False otherwise
            
        Raises:
            ValueError: If group is unknown
            RuntimeError: If experiment is not active
        """
        if group not in self.groups:
            raise ValueError(f"Unknown group: {group}")
        
        if self.status != ExperimentStatus.ACTIVE:
            raise RuntimeError(f"Experiment {self.name} is not active (status: {self.status.value})")
        
        return self.assignment_strategy.is_in_group(key, group)
    
    def activate(self) -> None:
        """Activate the experiment."""
        self.status = ExperimentStatus.ACTIVE
        self.updated_at = time.time()
    
    def pause(self) -> None:
        """Pause the experiment."""
        self.status = ExperimentStatus.PAUSED
        self.updated_at = time.time()
    
    def complete(self) -> None:
        """Complete the experiment."""
        self.status = ExperimentStatus.COMPLETED
        self.updated_at = time.time()
    
    def archive(self) -> None:
        """Archive the experiment."""
        self.status = ExperimentStatus.ARCHIVED
        self.updated_at = time.time()
    
    def update_metadata(self, metadata: Dict[str, str]) -> None:
        """Update experiment metadata.
        
        Args:
            metadata: New metadata to merge with existing
        """
        self.metadata.update(metadata)
        self.updated_at = time.time()
    
    def update_description(self, description: str) -> None:
        """Update experiment description.
        
        Args:
            description: New description
        """
        self.description = description
        self.updated_at = time.time()
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Get the state of the experiment as a dictionary.
        
        Returns:
            Dictionary of state
        """
        # Basic properties
        state = {
            "name": self.name,
            "description": self.description,
            "groups": self.groups,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "assignment_type": self.assignment_strategy.assignment_type.value
        }
        
        # Add strategy-specific properties
        if self.assignment_strategy.assignment_type == AssignmentType.PERCENTAGE:
            strategy = cast(PercentageAssignment, self.assignment_strategy)
            state["weights"] = strategy.weights
            state["salt"] = strategy.salt
            state["hash_seed"] = strategy.hash_seed
        
        elif self.assignment_strategy.assignment_type == AssignmentType.HASH_MOD:
            strategy = cast(HashModAssignment, self.assignment_strategy)
            state["salt"] = strategy.salt
            state["hash_seed"] = strategy.hash_seed
        
        elif self.assignment_strategy.assignment_type == AssignmentType.LIST_BASED:
            strategy = cast(ListBasedAssignment, self.assignment_strategy)
            # Convert sets to lists for serialization
            key_lists = {group: list(keys) for group, keys in strategy.key_lists.items()}
            state["key_lists"] = key_lists
            state["default_group"] = strategy.default_group
        
        return state
    
    @classmethod
    def from_state_dict(cls, state: Dict[str, Any]) -> "Experiment":
        """Create an experiment from a state dictionary.
        
        Args:
            state: Dictionary of state
            
        Returns:
            New Experiment instance
            
        Raises:
            ValueError: If state is invalid
        """
        assignment_type = state.get("assignment_type")
        if not assignment_type:
            raise ValueError("Missing assignment_type in state")
        
        if assignment_type == AssignmentType.PERCENTAGE.value:
            # Percentage-based experiment
            if "weights" not in state:
                raise ValueError("Missing weights for percentage-based experiment")
            
            return cls.create_percentage_based(
                name=state["name"],
                groups=state["groups"],
                weights=state["weights"],
                salt=state.get("salt", ""),
                hash_seed=state.get("hash_seed", 0),
                description=state.get("description", ""),
                metadata=state.get("metadata", {})
            )
        
        elif assignment_type == AssignmentType.HASH_MOD.value:
            # Hash-based experiment
            return cls.create_hash_based(
                name=state["name"],
                groups=state["groups"],
                salt=state.get("salt", ""),
                hash_seed=state.get("hash_seed", 0),
                description=state.get("description", ""),
                metadata=state.get("metadata", {})
            )
        
        elif assignment_type == AssignmentType.LIST_BASED.value:
            # List-based experiment
            if "key_lists" not in state:
                raise ValueError("Missing key_lists for list-based experiment")
            
            # Convert lists back to sets
            key_lists = {group: set(keys) for group, keys in state["key_lists"].items()}
            
            experiment = cls.create_list_based(
                name=state["name"],
                key_lists=key_lists,
                default_group=state.get("default_group"),
                description=state.get("description", ""),
                metadata=state.get("metadata", {})
            )
            
            # Set status and timestamps
            if "status" in state:
                experiment.status = ExperimentStatus(state["status"])
            if "created_at" in state:
                experiment.created_at = state["created_at"]
            if "updated_at" in state:
                experiment.updated_at = state["updated_at"]
            
            return experiment
        
        else:
            raise ValueError(f"Unknown assignment type: {assignment_type}")


class ExperimentGroup(BaseModel):
    """Group of related experiments."""
    
    name: str = Field(..., description="Group name")
    description: str = Field("", description="Group description")
    experiments: Set[str] = Field(default_factory=set, description="Set of experiment names")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")
    created_at: float = Field(default_factory=time.time, description="Unix timestamp when group was created")
    updated_at: float = Field(default_factory=time.time, description="Unix timestamp when group was last updated")
    
    def add_experiment(self, experiment_name: str) -> None:
        """Add an experiment to the group.
        
        Args:
            experiment_name: Name of experiment to add
        """
        self.experiments.add(experiment_name)
        self.updated_at = time.time()
    
    def remove_experiment(self, experiment_name: str) -> bool:
        """Remove an experiment from the group.
        
        Args:
            experiment_name: Name of experiment to remove
            
        Returns:
            True if the experiment was removed, False if it wasn't in the group
        """
        if experiment_name not in self.experiments:
            return False
        
        self.experiments.remove(experiment_name)
        self.updated_at = time.time()
        return True
    
    def update_metadata(self, metadata: Dict[str, str]) -> None:
        """Update group metadata.
        
        Args:
            metadata: New metadata to merge with existing
        """
        self.metadata.update(metadata)
        self.updated_at = time.time()
    
    def update_description(self, description: str) -> None:
        """Update group description.
        
        Args:
            description: New description
        """
        self.description = description
        self.updated_at = time.time()