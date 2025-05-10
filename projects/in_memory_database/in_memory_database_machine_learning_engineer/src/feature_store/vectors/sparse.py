"""
Sparse vector implementation optimized for ML feature representation.
"""

from typing import Dict, List, Optional, Tuple, Union, cast

import numpy as np
from pydantic import Field, validator

from feature_store.vectors.base import Distance, VectorBase
from feature_store.vectors.dense import DenseVector


class SparseVector(VectorBase):
    """
    Sparse vector implementation optimized for ML feature representation.
    
    This class represents a vector where most elements are zero, storing only
    non-zero elements for memory efficiency.
    """

    indices: np.ndarray = Field(..., description="Indices of non-zero values")
    values: np.ndarray = Field(..., description="Non-zero values")
    
    def __init__(
        self, 
        indices: Union[List[int], np.ndarray], 
        values: Union[List[float], np.ndarray],
        dimensionality: int,
        **kwargs
    ):
        """Initialize a sparse vector.
        
        Args:
            indices: Indices of non-zero values
            values: Non-zero values
            dimensionality: Total dimensionality of the vector
            **kwargs: Additional arguments passed to the parent class
        """
        if isinstance(indices, list):
            indices = np.array(indices, dtype=np.int32)
        
        if isinstance(values, list):
            values = np.array(values, dtype=np.float32)
        
        if len(indices) != len(values):
            raise ValueError(f"Length of indices ({len(indices)}) must match "
                            f"length of values ({len(values)})")
        
        # Ensure indices are sorted
        sort_idx = np.argsort(indices)
        indices = indices[sort_idx]
        values = values[sort_idx]
        
        super().__init__(
            indices=indices,
            values=values,
            dimensionality=dimensionality,
            **kwargs
        )
    
    @classmethod
    def from_dict(cls, data: Dict[int, float], dimensionality: int) -> "SparseVector":
        """Create a sparse vector from a dictionary of index-value pairs.
        
        Args:
            data: Dictionary mapping indices to values
            dimensionality: Total dimensionality of the vector
            
        Returns:
            A new SparseVector
        """
        indices = np.array(list(data.keys()), dtype=np.int32)
        values = np.array(list(data.values()), dtype=np.float32)
        
        # Sort by indices
        sort_idx = np.argsort(indices)
        indices = indices[sort_idx]
        values = values[sort_idx]
        
        return cls(indices=indices, values=values, dimensionality=dimensionality)
    
    @validator("indices")
    def validate_indices(cls, v):
        """Validate that indices is a 1D array of integers."""
        if not isinstance(v, np.ndarray):
            v = np.array(v, dtype=np.int32)
        
        if v.ndim != 1:
            raise ValueError(f"Indices must be a 1D array, got {v.ndim}D")
        
        return v.astype(np.int32)
    
    @validator("values")
    def validate_values(cls, v):
        """Validate that values is a 1D array of floating-point numbers."""
        if not isinstance(v, np.ndarray):
            v = np.array(v, dtype=np.float32)
        
        if v.ndim != 1:
            raise ValueError(f"Values must be a 1D array, got {v.ndim}D")
        
        return v.astype(np.float32)
    
    def to_array(self) -> np.ndarray:
        """Convert sparse vector to a dense numpy array.
        
        Returns:
            A dense numpy array representation of the vector
        """
        dense = np.zeros(self.dimensionality, dtype=np.float32)
        dense[self.indices] = self.values
        return dense
    
    def to_dict(self) -> Dict[int, float]:
        """Convert sparse vector to a dictionary.
        
        Returns:
            A dictionary mapping indices to values
        """
        return {int(idx): float(val) for idx, val in zip(self.indices, self.values)}
    
    def distance(self, other: VectorBase, metric: Distance = Distance.EUCLIDEAN) -> float:
        """Calculate distance between this vector and another.
        
        For sparse vectors, we have efficient implementations for
        some distance metrics that avoid materializing the full dense vectors.
        
        Args:
            other: Vector to calculate distance to
            metric: Distance metric to use
            
        Returns:
            Distance according to the specified metric
        """
        if isinstance(other, SparseVector):
            # For sparse-sparse distance, use specialized implementations
            if metric == Distance.EUCLIDEAN:
                return self._sparse_euclidean(other)
            elif metric == Distance.MANHATTAN:
                return self._sparse_manhattan(other)
            elif metric == Distance.DOT_PRODUCT:
                return self._sparse_dot_product(other)
        
        # Fall back to dense implementation
        return self.calculate_distance(self.to_array(), other.to_array(), metric)
    
    def _sparse_euclidean(self, other: "SparseVector") -> float:
        """Efficient Euclidean distance calculation between sparse vectors.
        
        Uses the identity: ||a-b||^2 = ||a||^2 + ||b||^2 - 2*a·b
        
        Args:
            other: Sparse vector to calculate distance to
            
        Returns:
            Euclidean distance
        """
        # Calculate ||a||^2
        self_squared_norm = np.sum(self.values ** 2)
        
        # Calculate ||b||^2
        other_squared_norm = np.sum(other.values ** 2)
        
        # Calculate a·b efficiently using only non-zero elements
        dot_product = self._sparse_dot_product_value(other)
        
        # Apply the formula
        distance_squared = self_squared_norm + other_squared_norm - 2 * dot_product
        
        # Handle potential floating point errors
        distance_squared = max(distance_squared, 0.0)
        
        return float(np.sqrt(distance_squared))
    
    def _sparse_manhattan(self, other: "SparseVector") -> float:
        """Efficient Manhattan distance calculation between sparse vectors.
        
        Args:
            other: Sparse vector to calculate distance to
            
        Returns:
            Manhattan distance
        """
        # Initialize with sum of absolute values in both vectors
        distance = np.sum(np.abs(self.values)) + np.sum(np.abs(other.values))
        
        # Subtract 2 * sum of min(a_i, b_i) for overlapping indices
        i, j = 0, 0
        while i < len(self.indices) and j < len(other.indices):
            if self.indices[i] == other.indices[j]:
                # Overlapping index, subtract the minimum absolute value twice
                # (once from each sum above)
                overlap = min(abs(self.values[i]), abs(other.values[j]))
                distance -= 2 * overlap
                i += 1
                j += 1
            elif self.indices[i] < other.indices[j]:
                i += 1
            else:
                j += 1
                
        return float(distance)
    
    def _sparse_dot_product(self, other: "SparseVector") -> float:
        """Efficient dot product distance calculation between sparse vectors.
        
        Args:
            other: Sparse vector to calculate distance to
            
        Returns:
            Negative dot product (as a distance)
        """
        return float(-self._sparse_dot_product_value(other))
    
    def _sparse_dot_product_value(self, other: "SparseVector") -> float:
        """Efficient dot product calculation between sparse vectors.
        
        Args:
            other: Sparse vector to calculate dot product with
            
        Returns:
            Dot product
        """
        # Merge-join the sorted indices
        result = 0.0
        i, j = 0, 0
        while i < len(self.indices) and j < len(other.indices):
            if self.indices[i] == other.indices[j]:
                result += self.values[i] * other.values[j]
                i += 1
                j += 1
            elif self.indices[i] < other.indices[j]:
                i += 1
            else:
                j += 1
                
        return float(result)
    
    def __len__(self) -> int:
        """Return the dimensionality of the vector.
        
        Returns:
            The dimensionality of the vector
        """
        return self.dimensionality
    
    def __getitem__(self, idx: Union[int, slice]) -> Union[float, "SparseVector", "DenseVector"]:
        """Get a value or slice of the vector.
        
        Args:
            idx: Index or slice to retrieve
            
        Returns:
            If idx is an integer, returns the value at that index.
            If idx is a slice, returns a new vector containing the sliced values.
        """
        if isinstance(idx, int):
            # For single index access, search for the index
            pos = np.searchsorted(self.indices, idx)
            if pos < len(self.indices) and self.indices[pos] == idx:
                return float(self.values[pos])
            return 0.0
        
        elif isinstance(idx, slice):
            # For slicing, convert to dense and then slice
            dense_sliced = self.to_array()[idx]
            return DenseVector(dense_sliced)
        
        raise TypeError(f"Invalid index type: {type(idx)}")
    
    def norm(self, p: int = 2) -> float:
        """Calculate the p-norm of the vector.
        
        For sparse vectors, this can be done efficiently using only non-zero elements.
        
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
    
    def __add__(self, other: Union["SparseVector", DenseVector]) -> Union["SparseVector", DenseVector]:
        """Add another vector to this one.
        
        Args:
            other: Vector to add
            
        Returns:
            If other is a SparseVector, returns a new SparseVector.
            If other is a DenseVector, returns a new DenseVector.
        """
        if isinstance(other, SparseVector):
            if self.dimensionality != other.dimensionality:
                raise ValueError(f"Cannot add vectors of different dimensions: "
                                f"{self.dimensionality} vs {other.dimensionality}")
            
            # Merge the indices and values
            result_dict = self.to_dict()
            for idx, val in zip(other.indices, other.values):
                idx_int = int(idx)
                if idx_int in result_dict:
                    result_dict[idx_int] += float(val)
                else:
                    result_dict[idx_int] = float(val)
            
            # Filter out zeros
            result_dict = {idx: val for idx, val in result_dict.items() if val != 0}
            
            return SparseVector.from_dict(result_dict, self.dimensionality)
        
        elif isinstance(other, DenseVector):
            if self.dimensionality != len(other):
                raise ValueError(f"Cannot add vectors of different dimensions: "
                                f"{self.dimensionality} vs {len(other)}")
            
            # Convert to dense and add
            return DenseVector(self.to_array() + other.to_array())
        
        raise TypeError(f"Cannot add {type(other)} to SparseVector")
    
    def __sub__(self, other: Union["SparseVector", DenseVector]) -> Union["SparseVector", DenseVector]:
        """Subtract another vector from this one.
        
        Args:
            other: Vector to subtract
            
        Returns:
            If other is a SparseVector, returns a new SparseVector.
            If other is a DenseVector, returns a new DenseVector.
        """
        if isinstance(other, SparseVector):
            if self.dimensionality != other.dimensionality:
                raise ValueError(f"Cannot subtract vectors of different dimensions: "
                                f"{self.dimensionality} vs {other.dimensionality}")
            
            # Merge the indices and values
            result_dict = self.to_dict()
            for idx, val in zip(other.indices, other.values):
                idx_int = int(idx)
                if idx_int in result_dict:
                    result_dict[idx_int] -= float(val)
                else:
                    result_dict[idx_int] = -float(val)
            
            # Filter out zeros
            result_dict = {idx: val for idx, val in result_dict.items() if val != 0}
            
            return SparseVector.from_dict(result_dict, self.dimensionality)
        
        elif isinstance(other, DenseVector):
            if self.dimensionality != len(other):
                raise ValueError(f"Cannot subtract vectors of different dimensions: "
                                f"{self.dimensionality} vs {len(other)}")
            
            # Convert to dense and subtract
            return DenseVector(self.to_array() - other.to_array())
        
        raise TypeError(f"Cannot subtract {type(other)} from SparseVector")
    
    def __mul__(self, scalar: float) -> "SparseVector":
        """Multiply vector by a scalar.
        
        Args:
            scalar: Value to multiply by
            
        Returns:
            A new SparseVector that is the product of the vector and scalar
        """
        if not isinstance(scalar, (int, float)):
            raise TypeError(f"Cannot multiply SparseVector by {type(scalar)}")
        
        if scalar == 0:
            # Return empty sparse vector
            return SparseVector(indices=np.array([], dtype=np.int32), 
                              values=np.array([], dtype=np.float32),
                              dimensionality=self.dimensionality)
        
        # Create a new sparse vector with scaled values
        return SparseVector(
            indices=self.indices.copy(),
            values=self.values * scalar,
            dimensionality=self.dimensionality
        )
    
    def __rmul__(self, scalar: float) -> "SparseVector":
        """Multiply vector by a scalar (right multiplication).
        
        Args:
            scalar: Value to multiply by
            
        Returns:
            A new SparseVector that is the product of the vector and scalar
        """
        return self.__mul__(scalar)
    
    def __truediv__(self, scalar: float) -> "SparseVector":
        """Divide vector by a scalar.
        
        Args:
            scalar: Value to divide by
            
        Returns:
            A new SparseVector that is the quotient of the vector and scalar
        """
        if not isinstance(scalar, (int, float)):
            raise TypeError(f"Cannot divide SparseVector by {type(scalar)}")
        
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide vector by zero")
        
        # Create a new sparse vector with scaled values
        return SparseVector(
            indices=self.indices.copy(),
            values=self.values / scalar,
            dimensionality=self.dimensionality
        )
    
    def dot(self, other: Union["SparseVector", DenseVector]) -> float:
        """Calculate dot product with another vector.
        
        Args:
            other: Vector to calculate dot product with
            
        Returns:
            Dot product of the two vectors
        """
        if isinstance(other, SparseVector):
            return self._sparse_dot_product_value(other)
        
        elif isinstance(other, DenseVector):
            if self.dimensionality != len(other):
                raise ValueError(f"Cannot calculate dot product of vectors with different dimensions: "
                               f"{self.dimensionality} vs {len(other)}")
            
            # For dot product with dense vector, use only the non-zero indices
            return float(np.sum(self.values * other.to_array()[self.indices]))
        
        raise TypeError(f"Cannot calculate dot product with {type(other)}")
    
    def __eq__(self, other: object) -> bool:
        """Check if two vectors are equal.
        
        Args:
            other: Object to compare with
            
        Returns:
            True if the vectors are equal, False otherwise
        """
        if not isinstance(other, SparseVector):
            return False
        
        if self.dimensionality != other.dimensionality:
            return False
        
        if len(self.indices) != len(other.indices):
            return False
        
        return bool(np.array_equal(self.indices, other.indices) and 
                  np.allclose(self.values, other.values))
    
    def __repr__(self) -> str:
        """Create a string representation of the vector.
        
        Returns:
            String representation
        """
        if len(self.indices) <= 6:
            elements = [f"{idx}:{val:.4f}" for idx, val in zip(self.indices, self.values)]
            elements_str = ", ".join(elements)
        else:
            # For long vectors, show first 3 and last 3 elements
            first = [f"{idx}:{val:.4f}" for idx, val in zip(self.indices[:3], self.values[:3])]
            last = [f"{idx}:{val:.4f}" for idx, val in zip(self.indices[-3:], self.values[-3:])]
            elements_str = ", ".join(first) + ", ..., " + ", ".join(last)
        
        density = len(self.indices) / self.dimensionality * 100
        return f"SparseVector({elements_str}, dim={self.dimensionality}, nnz={len(self.indices)}, density={density:.2f}%)"
    
    @property
    def nnz(self) -> int:
        """Get the number of non-zero elements.
        
        Returns:
            Number of non-zero elements
        """
        return len(self.indices)
    
    @property
    def density(self) -> float:
        """Get the density of the vector (percentage of non-zero elements).
        
        Returns:
            Density as a percentage
        """
        return len(self.indices) / self.dimensionality * 100