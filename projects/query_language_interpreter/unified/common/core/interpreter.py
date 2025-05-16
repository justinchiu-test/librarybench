"""Base interpreter functionality for query language interpreters."""

from typing import Any, Dict, List, Optional, Type, Union
from abc import ABC, abstractmethod

from common.core.query import BaseQuery, ExecutionContext
from common.core.result import QueryResult


class BaseInterpreter(ABC):
    """Base class for query interpreters."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize a base interpreter.

        Args:
            config: Interpreter configuration
        """
        self.config = config or {}
        self.services: Dict[str, Any] = {}

    @abstractmethod
    def parse(self, query_string: str) -> BaseQuery:
        """Parse query string into structured representation.

        Args:
            query_string: Query string to parse

        Returns:
            BaseQuery: Structured query representation
        """
        pass

    @abstractmethod
    def execute(self, query: BaseQuery) -> QueryResult:
        """Execute a structured query and return results.

        Args:
            query: Structured query to execute

        Returns:
            QueryResult: Query execution result
        """
        pass

    def validate(self, query: BaseQuery) -> bool:
        """Validate query against interpreter rules.

        Args:
            query: Query to validate

        Returns:
            bool: True if valid, False otherwise
        """
        # Basic validation, should be overridden by subclasses
        return query.validate()

    def register_service(self, name: str, service: Any) -> None:
        """Register a service with the interpreter.

        Args:
            name: Service name
            service: Service instance
        """
        self.services[name] = service

    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service.

        Args:
            name: Service name

        Returns:
            Optional[Any]: Service instance, or None if not found
        """
        return self.services.get(name)

    def parse_and_execute(self, query_string: str, user_id: str = None) -> QueryResult:
        """Parse and execute a query string.

        Args:
            query_string: Query string to parse and execute
            user_id: ID of the user executing the query

        Returns:
            QueryResult: Query execution result
        """
        # Parse the query
        query = self.parse(query_string)

        # Create execution context
        context = ExecutionContext(user_id=user_id)
        query.set_execution_context(context)

        # Validate the query
        if not self.validate(query):
            context.fail("Query validation failed")
            return QueryResult(
                query=query, success=False, error="Query validation failed"
            )

        # Execute the query
        try:
            context.start()
            result = self.execute(query)
            context.complete()
            return result
        except Exception as e:
            context.fail(str(e))
            return QueryResult(query=query, success=False, error=str(e))
