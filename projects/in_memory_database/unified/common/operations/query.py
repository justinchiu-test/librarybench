"""
Query interfaces and classes for the common library.

This module provides interfaces and classes for querying data in both vectordb
and syncdb implementations.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Set, TypeVar, Generic, Union, Tuple
import time
import json

T = TypeVar('T')


class QueryType(Enum):
    """
    Enum representing types of queries.
    """
    EXACT = "exact"  # Exact match queries
    RANGE = "range"  # Range queries (e.g., between two values)
    PREFIX = "prefix"  # Prefix queries (e.g., starts with)
    SUFFIX = "suffix"  # Suffix queries (e.g., ends with)
    CONTAINS = "contains"  # Contains queries (e.g., substring)
    REGEX = "regex"  # Regular expression queries
    FULLTEXT = "fulltext"  # Full-text search queries
    SIMILARITY = "similarity"  # Similarity/distance-based queries


class Operator(Enum):
    """
    Enum representing logical operators for combining filter conditions.
    """
    AND = "and"
    OR = "or"
    NOT = "not"


class FilterCondition:
    """
    Represents a condition for filtering records.
    
    This class defines the conditions used in queries to filter records based
    on field values.
    """
    
    def __init__(
        self,
        field_name: str,
        operator: QueryType,
        value: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize a filter condition.
        
        Args:
            field_name: The name of the field to filter on.
            operator: The operator to use for comparison.
            value: The value to compare against.
            metadata: Optional metadata for the condition.
        """
        self.field_name = field_name
        self.operator = operator
        self.value = value
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the filter condition to a dictionary representation.
        
        Returns:
            A dictionary containing the filter condition's data.
        """
        return {
            'field_name': self.field_name,
            'operator': self.operator.value,
            'value': self.value,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilterCondition':
        """
        Create a filter condition from a dictionary representation.
        
        Args:
            data: Dictionary containing filter condition data.
        
        Returns:
            A new FilterCondition instance.
        """
        return cls(
            field_name=data['field_name'],
            operator=QueryType(data['operator']),
            value=data['value'],
            metadata=data.get('metadata')
        )
    
    def matches(self, record: Any) -> bool:
        """
        Check if a record matches this filter condition.
        
        Args:
            record: The record to check against this condition.
        
        Returns:
            True if the record matches the condition, False otherwise.
        """
        # Get the field value from the record
        field_value = None
        
        # Try to get from attribute
        if hasattr(record, self.field_name):
            field_value = getattr(record, self.field_name)
        # Try to get from metadata
        elif hasattr(record, 'metadata') and self.field_name in record.metadata:
            field_value = record.metadata[self.field_name]
        # Try to get from dict-like access
        elif hasattr(record, '__getitem__'):
            try:
                field_value = record[self.field_name]
            except (KeyError, TypeError):
                pass
        
        # If we couldn't find the field, no match
        if field_value is None:
            return False
        
        # Check against the condition
        if self.operator == QueryType.EXACT:
            return field_value == self.value
        
        elif self.operator == QueryType.RANGE:
            if not isinstance(self.value, (list, tuple)) or len(self.value) != 2:
                return False
            min_val, max_val = self.value
            return min_val <= field_value <= max_val
        
        elif self.operator == QueryType.PREFIX:
            if not isinstance(field_value, str) or not isinstance(self.value, str):
                return False
            return field_value.startswith(self.value)
        
        elif self.operator == QueryType.SUFFIX:
            if not isinstance(field_value, str) or not isinstance(self.value, str):
                return False
            return field_value.endswith(self.value)
        
        elif self.operator == QueryType.CONTAINS:
            if isinstance(field_value, str) and isinstance(self.value, str):
                return self.value in field_value
            elif isinstance(field_value, (list, tuple, set)):
                return self.value in field_value
            return False
        
        elif self.operator == QueryType.REGEX:
            import re
            if not isinstance(field_value, str):
                return False
            try:
                return bool(re.search(self.value, field_value))
            except re.error:
                return False
        
        # For FULLTEXT and SIMILARITY, we need custom implementation
        return False


class QueryResult(Generic[T]):
    """
    Represents the result of a query.
    
    This class encapsulates the results of a query, including the matching
    records and metadata about the query execution.
    """
    
    def __init__(
        self,
        results: List[T],
        total_count: Optional[int] = None,
        execution_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize a query result.
        
        Args:
            results: The list of records that matched the query.
            total_count: The total number of matching records (may be different from
                        len(results) if pagination is used).
            execution_time: The time taken to execute the query, in seconds.
            metadata: Optional metadata about the query execution.
        """
        self.results = results
        self.total_count = total_count if total_count is not None else len(results)
        self.execution_time = execution_time
        self.metadata = metadata or {}
    
    def __len__(self) -> int:
        """
        Get the number of results.
        
        Returns:
            The number of results.
        """
        return len(self.results)
    
    def __iter__(self):
        """
        Iterate over the results.
        
        Returns:
            An iterator over the results.
        """
        return iter(self.results)
    
    def __getitem__(self, index):
        """
        Get a result by index.
        
        Args:
            index: The index of the result to get.
        
        Returns:
            The result at the specified index.
        """
        return self.results[index]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the query result to a dictionary representation.
        
        Returns:
            A dictionary containing the query result's data.
        """
        return {
            'results': [
                r.to_dict() if hasattr(r, 'to_dict') else r
                for r in self.results
            ],
            'total_count': self.total_count,
            'execution_time': self.execution_time,
            'metadata': self.metadata
        }


class Query(ABC):
    """
    Represents a query for retrieving records.
    
    This class defines the interface for queries that can be executed against
    a collection of records.
    """
    
    def __init__(
        self,
        filters: Optional[List[FilterCondition]] = None,
        filter_operator: Operator = Operator.AND,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Initialize a query.
        
        Args:
            filters: List of filter conditions to apply.
            filter_operator: Operator to use when combining filter conditions.
            limit: Maximum number of results to return.
            offset: Number of results to skip.
            sort_by: Field to sort results by.
            sort_order: Order to sort results in ("asc" or "desc").
            metadata: Optional metadata for the query.
        """
        self.filters = filters or []
        self.filter_operator = filter_operator
        self.limit = limit
        self.offset = offset
        self.sort_by = sort_by
        self.sort_order = sort_order.lower()
        self.metadata = metadata or {}
        self.created_at = time.time()
    
    def add_filter(self, filter_condition: FilterCondition) -> None:
        """
        Add a filter condition to the query.
        
        Args:
            filter_condition: The filter condition to add.
        """
        self.filters.append(filter_condition)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the query to a dictionary representation.
        
        Returns:
            A dictionary containing the query's data.
        """
        return {
            'filters': [f.to_dict() for f in self.filters],
            'filter_operator': self.filter_operator.value,
            'limit': self.limit,
            'offset': self.offset,
            'sort_by': self.sort_by,
            'sort_order': self.sort_order,
            'metadata': self.metadata,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Query':
        """
        Create a query from a dictionary representation.
        
        Args:
            data: Dictionary containing query data.
        
        Returns:
            A new Query instance.
        
        Note:
            This is just a basic implementation. Concrete query classes should
            override this method as needed.
        """
        filters = [
            FilterCondition.from_dict(f_data) 
            for f_data in data.get('filters', [])
        ]
        
        query = cls(
            filters=filters,
            filter_operator=Operator(data.get('filter_operator', 'and')),
            limit=data.get('limit'),
            offset=data.get('offset'),
            sort_by=data.get('sort_by'),
            sort_order=data.get('sort_order', 'asc'),
            metadata=data.get('metadata', {})
        )
        
        if 'created_at' in data:
            query.created_at = data['created_at']
        
        return query
    
    @abstractmethod
    def execute(self, collection: Any) -> QueryResult:
        """
        Execute the query against a collection.
        
        Args:
            collection: The collection to query against.
        
        Returns:
            A QueryResult containing the matching records and metadata.
        """
        pass