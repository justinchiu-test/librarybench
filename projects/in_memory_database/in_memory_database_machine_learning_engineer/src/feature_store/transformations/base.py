"""
Base transformation interface and common utilities.
"""

import hashlib
import json
import pickle
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import numpy as np
from pydantic import BaseModel, Field

from feature_store.vectors.base import VectorBase
from feature_store.vectors.dense import DenseVector
from feature_store.vectors.sparse import SparseVector


class Transformation(ABC, BaseModel):
    """
    Abstract base class for transformations.
    
    All transformation implementations must inherit from this class and implement
    the required methods.
    """

    name: str = Field(..., description="Transformation name")
    version: str = Field("1.0.0", description="Transformation version")
    is_fitted: bool = Field(False, description="Whether the transformation has been fitted")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        """Pydantic configuration."""
        
        arbitrary_types_allowed = True
    
    @abstractmethod
    def fit(self, vectors: List[VectorBase]) -> "Transformation":
        """Fit the transformation to the data.
        
        Args:
            vectors: List of vectors to fit the transformation to
            
        Returns:
            Self, for method chaining
        """
        pass
    
    @abstractmethod
    def transform(self, vector: VectorBase) -> VectorBase:
        """Apply the transformation to a vector.
        
        Args:
            vector: Vector to transform
            
        Returns:
            Transformed vector
        """
        pass
    
    @abstractmethod
    def inverse_transform(self, vector: VectorBase) -> VectorBase:
        """Apply the inverse transformation to a vector.
        
        Args:
            vector: Vector to inverse transform
            
        Returns:
            Inverse transformed vector
        """
        pass
    
    def transform_many(self, vectors: List[VectorBase]) -> List[VectorBase]:
        """Apply the transformation to multiple vectors.
        
        Default implementation applies transform to each vector individually.
        Subclasses should override this for more efficient batch processing.
        
        Args:
            vectors: List of vectors to transform
            
        Returns:
            List of transformed vectors
        """
        return [self.transform(v) for v in vectors]
    
    def inverse_transform_many(self, vectors: List[VectorBase]) -> List[VectorBase]:
        """Apply the inverse transformation to multiple vectors.
        
        Default implementation applies inverse_transform to each vector individually.
        Subclasses should override this for more efficient batch processing.
        
        Args:
            vectors: List of vectors to inverse transform
            
        Returns:
            List of inverse transformed vectors
        """
        return [self.inverse_transform(v) for v in vectors]
    
    def _check_is_fitted(self) -> None:
        """Check if the transformation is fitted.
        
        Raises:
            ValueError: If the transformation is not fitted
        """
        if not self.is_fitted:
            raise ValueError(f"Transformation {self.name} is not fitted")
    
    def get_state_dict(self) -> Dict[str, Any]:
        """Get the state of the transformation as a dictionary.
        
        Returns:
            Dictionary of state
        """
        # Start with model fields
        state = {
            "name": self.name,
            "version": self.version,
            "is_fitted": self.is_fitted,
            "metadata": self.metadata
        }
        
        # Add additional state specific to the transformation
        additional = self._get_additional_state()
        state.update(additional)
        
        return state
    
    def _get_additional_state(self) -> Dict[str, Any]:
        """Get additional state specific to the transformation.
        
        Returns:
            Dictionary of additional state
        """
        return {}
    
    def set_state_dict(self, state: Dict[str, Any]) -> None:
        """Set the state of the transformation from a dictionary.
        
        Args:
            state: Dictionary of state
        """
        # Set model fields
        self.name = state["name"]
        self.version = state["version"]
        self.is_fitted = state["is_fitted"]
        self.metadata = state["metadata"]
        
        # Set additional state specific to the transformation
        self._set_additional_state(state)
    
    def _set_additional_state(self, state: Dict[str, Any]) -> None:
        """Set additional state specific to the transformation.
        
        Args:
            state: Dictionary of state
        """
        pass
    
    def compute_hash(self) -> str:
        """Compute a hash of the transformation state.
        
        Used for detecting changes to the transformation.
        
        Returns:
            SHA-256 hash as a hexadecimal string
        """
        # Serialize state to bytes
        state = self.get_state_dict()
        
        # Convert to JSON string (handle numpy arrays)
        def json_numpy_handler(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        state_json = json.dumps(state, sort_keys=True, default=json_numpy_handler)
        
        # Compute hash
        return hashlib.sha256(state_json.encode()).hexdigest()
    
    def clone(self) -> "Transformation":
        """Create a deep copy of this transformation.
        
        Returns:
            A new instance with the same parameters but not fitted
        """
        # Serialize and deserialize
        return pickle.loads(pickle.dumps(self))
    
    def __repr__(self) -> str:
        """String representation.
        
        Returns:
            String representation
        """
        return f"{self.__class__.__name__}(name='{self.name}', version='{self.version}', fitted={self.is_fitted})"