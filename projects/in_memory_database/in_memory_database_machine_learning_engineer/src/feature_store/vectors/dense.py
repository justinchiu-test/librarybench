"""
Dense vector implementation optimized for ML feature representation.
"""

from typing import List, Optional, Union, cast

import numpy as np
from pydantic import Field, validator

from feature_store.vectors.base import Distance, VectorBase


class DenseVector(VectorBase):
    """
    Dense vector implementation optimized for ML feature representation.
    
    This class represents a vector with values for all dimensions, and is
    optimized for operations with dense feature vectors.
    """

    values: np.ndarray = Field(..., description="Vector values")
    
    def __init__(self, values: Union[List[float], np.ndarray], **kwargs):
        """Initialize a dense vector.
        
        Args:
            values: Vector values as a list or numpy array
            **kwargs: Additional arguments passed to the parent class
        """
        if isinstance(values, list):
            values = np.array(values, dtype=np.float32)
        
        super().__init__(
            values=values,
            dimensionality=len(values),
            **kwargs
        )
    
    @validator("values")
    def validate_values(cls, v):
        """Validate that values is a 1D array of floating-point numbers."""
        if not isinstance(v, np.ndarray):
            v = np.array(v, dtype=np.float32)
        
        if v.ndim != 1:
            raise ValueError(f"Values must be a 1D array, got {v.ndim}D")
        
        return v.astype(np.float32)
    
    def to_array(self) -> np.ndarray:
        """Convert vector to a dense numpy array.
        
        Returns:
            A numpy array representation of the vector
        """
        return self.values
    
    def distance(self, other: VectorBase, metric: Distance = Distance.EUCLIDEAN) -> float:
        """Calculate distance between this vector and another.
        
        Args:
            other: Vector to calculate distance to
            metric: Distance metric to use
            
        Returns:
            Distance according to the specified metric
        """
        if not isinstance(other, VectorBase):
            raise TypeError(f"Cannot calculate distance to {type(other)}")
        
        other_array = other.to_array()
        
        # Make sure dimensions match
        if len(self.values) != len(other_array):
            raise ValueError(f"Cannot calculate distance between vectors of different "
                            f"dimensions: {len(self.values)} vs {len(other_array)}")
        
        return self.calculate_distance(self.values, other_array, metric)
    
    def __len__(self) -> int:
        """Return the dimensionality of the vector.
        
        Returns:
            The dimensionality of the vector
        """
        return self.dimensionality
    
    def __getitem__(self, idx: Union[int, slice]) -> Union[float, "DenseVector"]:
        """Get a value or slice of the vector.
        
        Args:
            idx: Index or slice to retrieve
            
        Returns:
            If idx is an integer, returns the value at that index.
            If idx is a slice, returns a new DenseVector containing the sliced values.
        """
        if isinstance(idx, int):
            return float(self.values[idx])
        elif isinstance(idx, slice):
            sliced_values = self.values[idx]
            return DenseVector(sliced_values)
        raise TypeError(f"Invalid index type: {type(idx)}")
    
    def norm(self, p: int = 2) -> float:
        """Calculate the p-norm of the vector.
        
        Args:
            p: Order of the norm (1 for L1, 2 for L2, etc.)
            
        Returns:
            The p-norm of the vector
        """
        if p == 1:
            return float(np.sum(np.abs(self.values)))
        elif p == 2:
            return float(np.sqrt(np.sum(self.values ** 2)))
        else:
            return float(np.sum(np.abs(self.values) ** p) ** (1/p))
            
    def __add__(self, other: "DenseVector") -> "DenseVector":
        """Add two vectors together.
        
        Args:
            other: Vector to add
            
        Returns:
            A new DenseVector that is the sum of the two vectors
        """
        if not isinstance(other, DenseVector):
            raise TypeError(f"Cannot add {type(other)} to DenseVector")
        
        if len(self) != len(other):
            raise ValueError(f"Cannot add vectors of different dimensions: {len(self)} vs {len(other)}")
        
        return DenseVector(self.values + other.values)
    
    def __sub__(self, other: "DenseVector") -> "DenseVector":
        """Subtract another vector from this one.
        
        Args:
            other: Vector to subtract
            
        Returns:
            A new DenseVector that is the difference of the two vectors
        """
        if not isinstance(other, DenseVector):
            raise TypeError(f"Cannot subtract {type(other)} from DenseVector")
        
        if len(self) != len(other):
            raise ValueError(f"Cannot subtract vectors of different dimensions: {len(self)} vs {len(other)}")
        
        return DenseVector(self.values - other.values)
    
    def __mul__(self, scalar: float) -> "DenseVector":
        """Multiply vector by a scalar.
        
        Args:
            scalar: Value to multiply by
            
        Returns:
            A new DenseVector that is the product of the vector and scalar
        """
        if not isinstance(scalar, (int, float)):
            raise TypeError(f"Cannot multiply DenseVector by {type(scalar)}")
        
        return DenseVector(self.values * scalar)
    
    def __rmul__(self, scalar: float) -> "DenseVector":
        """Multiply vector by a scalar (right multiplication).
        
        Args:
            scalar: Value to multiply by
            
        Returns:
            A new DenseVector that is the product of the vector and scalar
        """
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar: float) -> "DenseVector":
        """Divide vector by a scalar.
        
        Args:
            scalar: Value to divide by
            
        Returns:
            A new DenseVector that is the quotient of the vector and scalar
        """
        if not isinstance(scalar, (int, float)):
            raise TypeError(f"Cannot divide DenseVector by {type(scalar)}")
        
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide vector by zero")
        
        return DenseVector(self.values / scalar)
    
    def dot(self, other: "DenseVector") -> float:
        """Calculate dot product with another vector.
        
        Args:
            other: Vector to calculate dot product with
            
        Returns:
            Dot product of the two vectors
        """
        if not isinstance(other, DenseVector):
            raise TypeError(f"Cannot calculate dot product with {type(other)}")
        
        if len(self) != len(other):
            raise ValueError(f"Cannot calculate dot product of vectors with different dimensions: {len(self)} vs {len(other)}")
        
        return float(np.dot(self.values, other.values))
    
    def __eq__(self, other: object) -> bool:
        """Check if two vectors are equal.
        
        Args:
            other: Object to compare with
            
        Returns:
            True if the vectors are equal, False otherwise
        """
        if not isinstance(other, DenseVector):
            return False
        
        if len(self) != len(other):
            return False
        
        return bool(np.allclose(self.values, other.values))
    
    def __repr__(self) -> str:
        """Create a string representation of the vector.
        
        Returns:
            String representation
        """
        if len(self.values) <= 6:
            values_str = np.array2string(self.values, precision=4, separator=", ")
        else:
            # For long vectors, show first 3 and last 3 elements
            first = np.array2string(self.values[:3], precision=4, separator=", ")
            last = np.array2string(self.values[-3:], precision=4, separator=", ")
            values_str = f"{first[:-1]}, ..., {last[1:]}"
        
        return f"DenseVector({values_str}, dim={self.dimensionality})"