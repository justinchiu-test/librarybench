"""
Transformation pipeline for chaining multiple transformations.
"""

import time
from typing import Dict, List, Optional, Tuple, Union, cast, Any

import numpy as np
from pydantic import Field

from feature_store.transformations.base import Transformation
from feature_store.vectors.base import VectorBase


class TransformationPipeline(Transformation):
    """
    Pipeline for chaining multiple transformations.
    
    This transformer applies a sequence of transformations in order.
    """

    name: str = Field("pipeline", const=True)
    steps: List[Transformation] = Field(..., description="Sequence of transformations to apply")
    cache_enabled: bool = Field(True, description="Whether to cache intermediate results")
    _cache: Dict[str, Dict[str, VectorBase]] = Field(default_factory=dict, description="Cache for transformed vectors")
    _cache_timestamp: Dict[str, float] = Field(default_factory=dict, description="Timestamp for cached vectors")
    _cache_ttl: float = Field(300.0, description="Cache time-to-live in seconds")
    
    def fit(self, vectors: List[VectorBase]) -> "TransformationPipeline":
        """Fit the transformer to the data.
        
        Fits each transformation in the pipeline in order, transforming the
        data with each fitted transformation before fitting the next one.
        
        Args:
            vectors: List of vectors to fit the transformation to
            
        Returns:
            Self, for method chaining
        """
        if not vectors:
            raise ValueError("Cannot fit TransformationPipeline on empty list")
        
        X = vectors
        
        for step in self.steps:
            step.fit(X)
            X = step.transform_many(X)
        
        self.is_fitted = True
        self.clear_cache()
        return self
    
    def transform(self, vector: VectorBase) -> VectorBase:
        """Apply the transformation to a vector.
        
        Args:
            vector: Vector to transform
            
        Returns:
            Transformed vector
        """
        self._check_is_fitted()
        
        # Check cache first
        vector_hash = str(hash(str(vector.to_array().tobytes())))
        if self.cache_enabled and vector_hash in self._cache:
            # Check if cache is still valid
            if time.time() - self._cache_timestamp[vector_hash] <= self._cache_ttl:
                if "transformed" in self._cache[vector_hash]:
                    return self._cache[vector_hash]["transformed"]
        
        # Initialize cache entry if needed
        if self.cache_enabled and vector_hash not in self._cache:
            self._cache[vector_hash] = {}
            self._cache_timestamp[vector_hash] = time.time()
        
        # Apply each transformation in sequence
        X = vector
        for i, step in enumerate(self.steps):
            X = step.transform(X)
            
            # Cache intermediate results if enabled
            if self.cache_enabled and i < len(self.steps) - 1:
                self._cache[vector_hash][f"step_{i}"] = X
        
        # Cache final result
        if self.cache_enabled:
            self._cache[vector_hash]["transformed"] = X
        
        return X
    
    def inverse_transform(self, vector: VectorBase) -> VectorBase:
        """Apply the inverse transformation to a vector.
        
        Args:
            vector: Vector to inverse transform
            
        Returns:
            Inverse transformed vector
        """
        self._check_is_fitted()
        
        # Check cache first
        vector_hash = str(hash(str(vector.to_array().tobytes())))
        if self.cache_enabled and vector_hash in self._cache:
            # Check if cache is still valid
            if time.time() - self._cache_timestamp[vector_hash] <= self._cache_ttl:
                if "inverse_transformed" in self._cache[vector_hash]:
                    return self._cache[vector_hash]["inverse_transformed"]
        
        # Initialize cache entry if needed
        if self.cache_enabled and vector_hash not in self._cache:
            self._cache[vector_hash] = {}
            self._cache_timestamp[vector_hash] = time.time()
        
        # Apply each transformation in reverse sequence
        X = vector
        for i, step in reversed(list(enumerate(self.steps))):
            X = step.inverse_transform(X)
            
            # Cache intermediate results if enabled
            if self.cache_enabled and i > 0:
                self._cache[vector_hash][f"inverse_step_{i}"] = X
        
        # Cache final result
        if self.cache_enabled:
            self._cache[vector_hash]["inverse_transformed"] = X
        
        return X
    
    def transform_many(self, vectors: List[VectorBase]) -> List[VectorBase]:
        """Apply the transformation to multiple vectors.
        
        Args:
            vectors: List of vectors to transform
            
        Returns:
            List of transformed vectors
        """
        self._check_is_fitted()
        
        X = vectors
        
        for step in self.steps:
            X = step.transform_many(X)
        
        return X
    
    def inverse_transform_many(self, vectors: List[VectorBase]) -> List[VectorBase]:
        """Apply the inverse transformation to multiple vectors.
        
        Args:
            vectors: List of vectors to inverse transform
            
        Returns:
            List of inverse transformed vectors
        """
        self._check_is_fitted()
        
        X = vectors
        
        for step in reversed(self.steps):
            X = step.inverse_transform_many(X)
        
        return X
    
    def clear_cache(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        self._cache_timestamp.clear()
    
    def set_cache_ttl(self, ttl: float) -> None:
        """Set the cache time-to-live.
        
        Args:
            ttl: Time-to-live in seconds
        """
        self._cache_ttl = ttl
    
    def enable_cache(self) -> None:
        """Enable caching."""
        self.cache_enabled = True
    
    def disable_cache(self) -> None:
        """Disable caching."""
        self.cache_enabled = False
        self.clear_cache()
    
    def _get_additional_state(self) -> Dict[str, Any]:
        """Get additional state specific to the transformation.
        
        Returns:
            Dictionary of additional state
        """
        return {
            "steps": [step.get_state_dict() for step in self.steps],
            "cache_enabled": self.cache_enabled,
            "cache_ttl": self._cache_ttl
        }
    
    def _set_additional_state(self, state: Dict[str, Any]) -> None:
        """Set additional state specific to the transformation.
        
        Args:
            state: Dictionary of state
        """
        self.cache_enabled = state["cache_enabled"]
        self._cache_ttl = state["cache_ttl"]
        
        # Recreate steps (this would require knowing the class of each step)
        # For a full implementation, we'd need a registry of transformation types
        # This is a simplified version
        self.steps = []