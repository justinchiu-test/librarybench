"""
Transformation interfaces and classes for the common library.

This module provides interfaces and base classes for transformations that can be
applied to data in both vectordb and syncdb implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable, Union, Sequence
import json
import time
import copy

from ..core.base import BaseOperation


T = TypeVar('T')
U = TypeVar('U')


class Operation(BaseOperation, Generic[T, U]):
    """
    Represents a basic operation that transforms input data of type T to output data of type U.
    
    This class is a generic operation that can be applied to various types of data.
    """
    
    def __init__(
        self, 
        name: str, 
        operation_fn: Callable[[T], U],
        description: Optional[str] = None
    ) -> None:
        """
        Initialize an operation.
        
        Args:
            name: The name of the operation.
            operation_fn: The function that performs the transformation.
            description: Optional description of the operation.
        """
        super().__init__(name, description)
        self.operation_fn = operation_fn
    
    def execute(self, data: T) -> U:
        """
        Execute the operation on the input data.
        
        Args:
            data: The input data to transform.
        
        Returns:
            The transformed data.
        """
        return self.operation_fn(data)
    
    def __call__(self, data: T) -> U:
        """
        Make the operation callable.
        
        Args:
            data: The input data to transform.
        
        Returns:
            The transformed data.
        """
        return self.execute(data)


class Transformer(ABC, Generic[T, U]):
    """
    Interface for transformers that convert data from one type to another.
    
    Transformers are used for various purposes, such as normalizing data,
    converting between formats, etc.
    """
    
    def __init__(
        self, 
        name: str, 
        description: Optional[str] = None
    ) -> None:
        """
        Initialize a transformer.
        
        Args:
            name: The name of the transformer.
            description: Optional description of the transformer.
        """
        self.name = name
        self.description = description
        self.created_at = time.time()
    
    @abstractmethod
    def transform(self, data: T) -> U:
        """
        Transform the input data.
        
        Args:
            data: The input data to transform.
        
        Returns:
            The transformed data.
        """
        pass
    
    def __call__(self, data: T) -> U:
        """
        Make the transformer callable.
        
        Args:
            data: The input data to transform.
        
        Returns:
            The transformed data.
        """
        return self.transform(data)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the transformer to a dictionary representation.
        
        Returns:
            A dictionary containing the transformer's metadata.
        """
        return {
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'type': self.__class__.__name__
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transformer':
        """
        Create a transformer from a dictionary representation.
        
        Args:
            data: Dictionary containing transformer metadata.
        
        Returns:
            A new Transformer instance.
        
        Note:
            This is a basic implementation that only sets metadata. Subclasses
            that have additional parameters should override this method.
        """
        transformer = cls(
            name=data['name'],
            description=data.get('description')
        )
        transformer.created_at = data.get('created_at', time.time())
        return transformer


V = TypeVar('V')


class Pipeline(Transformer[T, V]):
    """
    A pipeline of transformers that are applied in sequence.
    
    This allows for composing multiple transformations into a single operation.
    """
    
    def __init__(
        self, 
        name: str, 
        transformers: List[Transformer],
        description: Optional[str] = None
    ) -> None:
        """
        Initialize a pipeline.
        
        Args:
            name: The name of the pipeline.
            transformers: The list of transformers to apply in sequence.
            description: Optional description of the pipeline.
        """
        super().__init__(name, description)
        self.transformers = transformers
    
    def transform(self, data: T) -> V:
        """
        Transform the input data through the pipeline.
        
        Each transformer in the pipeline is applied in sequence, with the output
        of one transformer becoming the input to the next.
        
        Args:
            data: The input data to transform.
        
        Returns:
            The transformed data after passing through all transformers.
        """
        result = data
        for transformer in self.transformers:
            result = transformer.transform(result)
        return result
    
    def add_transformer(self, transformer: Transformer) -> None:
        """
        Add a transformer to the end of the pipeline.
        
        Args:
            transformer: The transformer to add.
        """
        self.transformers.append(transformer)
    
    def remove_transformer(self, index: int) -> Optional[Transformer]:
        """
        Remove a transformer from the pipeline.
        
        Args:
            index: The index of the transformer to remove.
        
        Returns:
            The removed transformer, or None if the index is out of range.
        """
        if 0 <= index < len(self.transformers):
            return self.transformers.pop(index)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the pipeline to a dictionary representation.
        
        Returns:
            A dictionary containing the pipeline's data.
        """
        result = super().to_dict()
        result['transformers'] = [
            transformer.to_dict() for transformer in self.transformers
        ]
        return result