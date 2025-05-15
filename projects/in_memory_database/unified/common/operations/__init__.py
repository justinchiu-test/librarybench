"""
Operations interfaces for the common library.

This package provides interfaces and base classes for operations that can be
performed on data in both vectordb and syncdb implementations.
"""

from .transform import (
    Transformer,
    Pipeline,
    Operation
)

from .query import (
    Query,
    QueryResult,
    QueryType,
    FilterCondition,
    Operator
)

__all__ = [
    # Transform
    "Transformer",
    "Pipeline",
    "Operation",
    
    # Query
    "Query",
    "QueryResult",
    "QueryType",
    "FilterCondition",
    "Operator"
]