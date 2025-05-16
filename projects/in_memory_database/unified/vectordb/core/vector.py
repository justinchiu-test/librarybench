"""
Vector data type implementation optimized for ML operations.
"""
from typing import List, Union, Tuple, Iterable, Dict, Any, Optional
import math
import json

from common.core import BaseRecord, Serializable


class Vector(BaseRecord, Serializable):
    """
    Vector data type with optimized operations for machine learning.
    
    This class implements a high-dimensional vector optimized for ML
    operations, with support for common vector operations and serialization.
    """
    
    def __init__(
        self, 
        values: Union[List[float], Tuple[float, ...]],
        id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None
    ):
        """
        Initialize a vector with values.
        
        Args:
            values: List or tuple of float values representing the vector.
            id: Optional identifier for the vector.
            metadata: Optional metadata associated with the vector.
            created_at: Timestamp when the vector was created. If None, current time is used.
            updated_at: Timestamp when the vector was last updated. If None, created_at is used.
        
        Raises:
            ValueError: If values is empty or contains non-numeric values.
        """
        if not values:
            raise ValueError("Vector cannot be empty")
        
        try:
            self._values = tuple(float(v) for v in values)
        except (ValueError, TypeError):
            raise ValueError("Vector values must be numeric")
            
        self._dimension = len(self._values)
        
        # Initialize BaseRecord with explicitly passing None for id if not provided
        # This will prevent BaseRecord from auto-generating an ID when one isn't provided
        super().__init__(id=id, metadata=metadata, created_at=created_at, updated_at=updated_at)
        
    @property
    def values(self) -> Tuple[float, ...]:
        """Get the vector values as a tuple."""
        return self._values
        
    @property
    def dimension(self) -> int:
        """Get the dimension of the vector."""
        return self._dimension
        
    def __len__(self) -> int:
        """Return the dimension of the vector."""
        return self._dimension
        
    def __getitem__(self, index: int) -> float:
        """Get the value at the specified index."""
        return self._values[index]
        
    def __iter__(self) -> Iterable[float]:
        """Iterate over the vector values."""
        return iter(self._values)
        
    def __eq__(self, other: object) -> bool:
        """Check if two vectors are equal."""
        if not isinstance(other, Vector):
            return False
        # Check if IDs are the same (inherit from BaseRecord)
        if super().__eq__(other) and self.id is not None:
            return True
        # Otherwise check if values are the same
        return self._values == other.values
    
    def __ne__(self, other: object) -> bool:
        """Check if two vectors are not equal."""
        return not self.__eq__(other)
        
    def __repr__(self) -> str:
        """Return a string representation of the vector."""
        if self.id:
            return f"Vector(id={self.id}, dimension={self._dimension})"
        return f"Vector(dimension={self._dimension})"
        
    def __str__(self) -> str:
        """Return a readable string representation of the vector."""
        # Convert tuple to list for string representation
        if len(self._values) > 6:
            # For long vectors, show first 3 and last 3 elements
            first_part = list(self._values[:3])
            last_part = list(self._values[-3:])
            values_str = f"{first_part} ... {last_part}"
        else:
            # For short vectors, show all elements
            values_str = str(list(self._values))
        
        if self.id:
            return f"Vector(id={self.id}, values={values_str})"
        return f"Vector(values={values_str})"
    
    def dot(self, other: 'Vector') -> float:
        """
        Calculate the dot product with another vector.
        
        Args:
            other: Another vector of the same dimension.
            
        Returns:
            The dot product of the two vectors.
            
        Raises:
            ValueError: If the vectors have different dimensions.
        """
        if self._dimension != other.dimension:
            raise ValueError(f"Cannot calculate dot product of vectors with different dimensions: {self._dimension} and {other.dimension}")
        
        return sum(a * b for a, b in zip(self._values, other.values))
    
    def magnitude(self) -> float:
        """
        Calculate the magnitude (L2 norm) of the vector.
        
        Returns:
            The magnitude of the vector.
        """
        return math.sqrt(sum(x * x for x in self._values))
    
    def normalize(self) -> 'Vector':
        """
        Create a normalized version of this vector (unit vector).
        
        Returns:
            A new Vector with unit magnitude.
            
        Raises:
            ValueError: If the vector has zero magnitude.
        """
        mag = self.magnitude()
        if math.isclose(mag, 0):
            raise ValueError("Cannot normalize a zero vector")
        
        return Vector([x / mag for x in self._values], self.id, self.metadata.copy())
    
    def add(self, other: 'Vector') -> 'Vector':
        """
        Add another vector to this one.
        
        Args:
            other: Another vector of the same dimension.
            
        Returns:
            A new Vector representing the sum.
            
        Raises:
            ValueError: If the vectors have different dimensions.
        """
        if self._dimension != other.dimension:
            raise ValueError(f"Cannot add vectors with different dimensions: {self._dimension} and {other.dimension}")
        
        return Vector([a + b for a, b in zip(self._values, other.values)])
    
    def subtract(self, other: 'Vector') -> 'Vector':
        """
        Subtract another vector from this one.
        
        Args:
            other: Another vector of the same dimension.
            
        Returns:
            A new Vector representing the difference.
            
        Raises:
            ValueError: If the vectors have different dimensions.
        """
        if self._dimension != other.dimension:
            raise ValueError(f"Cannot subtract vectors with different dimensions: {self._dimension} and {other.dimension}")
        
        return Vector([a - b for a, b in zip(self._values, other.values)])
    
    def scale(self, scalar: float) -> 'Vector':
        """
        Multiply the vector by a scalar value.
        
        Args:
            scalar: The scaling factor.
            
        Returns:
            A new Vector representing the scaled vector.
        """
        return Vector([x * scalar for x in self._values], self.id, self.metadata.copy())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the vector to a dictionary representation.
        
        Returns:
            A dictionary with the vector's data.
        """
        # Start with the base record data
        result = super().to_dict()
        # Add vector-specific data
        result["values"] = list(self._values)
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vector':
        """
        Create a vector from a dictionary representation.
        
        Args:
            data: Dictionary containing vector data.
        
        Returns:
            A new Vector instance.
        
        Raises:
            ValueError: If the dictionary is missing required fields.
        """
        if "values" not in data:
            raise ValueError("Dictionary must contain 'values' field")
        
        return cls(
            values=data["values"],
            id=data.get("id"),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )