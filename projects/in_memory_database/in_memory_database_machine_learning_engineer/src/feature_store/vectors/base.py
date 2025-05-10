"""
Base vector classes and distance metrics.
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol, Tuple, Union, cast

import numpy as np
from pydantic import BaseModel, Field


class Distance(Enum):
    """Supported distance metrics."""

    EUCLIDEAN = auto()
    COSINE = auto()
    MANHATTAN = auto()
    MAHALANOBIS = auto()
    DOT_PRODUCT = auto()  # Negative dot product (higher is more similar)


class VectorBase(ABC, BaseModel):
    """
    Abstract base class for vector types.
    
    All vector implementations must inherit from this class and implement
    the required methods.
    """

    dimensionality: int = Field(..., description="Dimensionality of the vector")
    
    class Config:
        """Pydantic configuration."""
        
        frozen = True
        arbitrary_types_allowed = True
    
    @abstractmethod
    def to_array(self) -> np.ndarray:
        """Convert vector to a dense numpy array."""
        pass
    
    @abstractmethod
    def distance(self, other: "VectorBase", metric: Distance = Distance.EUCLIDEAN) -> float:
        """Calculate distance between this vector and another."""
        pass
    
    @abstractmethod
    def __len__(self) -> int:
        """Return the dimensionality of the vector."""
        pass
    
    @abstractmethod
    def __getitem__(self, idx: Union[int, slice]) -> Union[float, "VectorBase"]:
        """Get a value or slice of the vector."""
        pass
    
    @abstractmethod
    def norm(self, p: int = 2) -> float:
        """Calculate the p-norm of the vector.
        
        Args:
            p: Order of the norm (1 for L1, 2 for L2, etc.)
            
        Returns:
            The p-norm of the vector
        """
        pass
    
    @staticmethod
    def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
        """Calculate Euclidean (L2) distance between two vectors.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            Euclidean distance
        """
        return float(np.sqrt(np.sum((a - b) ** 2)))
    
    @staticmethod
    def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine distance between two vectors.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            Cosine distance (1 - cosine similarity)
        """
        a_norm = np.linalg.norm(a)
        b_norm = np.linalg.norm(b)
        
        # Handle zero vectors
        if a_norm == 0 or b_norm == 0:
            return 1.0  # Maximum distance
            
        similarity = np.dot(a, b) / (a_norm * b_norm)
        # Handle floating point errors that could push similarity outside [-1, 1]
        similarity = max(min(similarity, 1.0), -1.0)
        return float(1.0 - similarity)
    
    @staticmethod
    def manhattan_distance(a: np.ndarray, b: np.ndarray) -> float:
        """Calculate Manhattan (L1) distance between two vectors.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            Manhattan distance
        """
        return float(np.sum(np.abs(a - b)))
    
    @staticmethod
    def mahalanobis_distance(a: np.ndarray, b: np.ndarray, 
                             cov_inv: Optional[np.ndarray] = None) -> float:
        """Calculate Mahalanobis distance between two vectors.
        
        Args:
            a: First vector
            b: Second vector
            cov_inv: Inverse of the covariance matrix. If None, will use identity
                     (equivalent to normalized Euclidean distance)
            
        Returns:
            Mahalanobis distance
        """
        diff = a - b
        if cov_inv is None:
            # Use identity matrix (normalized Euclidean)
            return float(np.sqrt(np.sum(diff * diff)))
        return float(np.sqrt(diff @ cov_inv @ diff))
    
    @staticmethod
    def dot_product_distance(a: np.ndarray, b: np.ndarray) -> float:
        """Calculate negative dot product as a distance.
        
        For this metric, lower values indicate higher similarity.
        
        Args:
            a: First vector
            b: Second vector
            
        Returns:
            Negative dot product
        """
        return float(-np.dot(a, b))
    
    @classmethod
    def calculate_distance(cls, a: np.ndarray, b: np.ndarray, 
                           metric: Distance = Distance.EUCLIDEAN, 
                           cov_inv: Optional[np.ndarray] = None) -> float:
        """Calculate distance between two vectors using specified metric.
        
        Args:
            a: First vector
            b: Second vector
            metric: Distance metric to use
            cov_inv: Inverse of the covariance matrix (for Mahalanobis distance)
            
        Returns:
            Distance according to the specified metric
        """
        if a.shape != b.shape:
            raise ValueError(f"Cannot calculate distance between vectors of different "
                            f"shapes: {a.shape} vs {b.shape}")
        
        if metric == Distance.EUCLIDEAN:
            return cls.euclidean_distance(a, b)
        elif metric == Distance.COSINE:
            return cls.cosine_distance(a, b)
        elif metric == Distance.MANHATTAN:
            return cls.manhattan_distance(a, b)
        elif metric == Distance.MAHALANOBIS:
            return cls.mahalanobis_distance(a, b, cov_inv)
        elif metric == Distance.DOT_PRODUCT:
            return cls.dot_product_distance(a, b)
        else:
            raise ValueError(f"Unsupported distance metric: {metric}")