"""Base query models and interfaces for query language interpreters."""

from typing import Any, Dict, List, Optional, Set, Union
from datetime import datetime


class ExecutionContext:
    """Context for query execution."""

    def __init__(
        self,
        user_id: str = None,
        start_time: datetime = None,
        end_time: datetime = None,
        status: str = "pending",
        error: str = None,
    ):
        """Initialize an execution context.

        Args:
            user_id: ID of the user executing the query
            start_time: Time when query execution started
            end_time: Time when query execution completed
            status: Current status of the query execution
            error: Error message if execution failed
        """
        self.user_id = user_id
        self.start_time = start_time or datetime.now()
        self.end_time = end_time
        self.status = status
        self.error = error
        self.metadata: Dict[str, Any] = {}

    def start(self) -> None:
        """Start query execution."""
        self.start_time = datetime.now()
        self.status = "running"

    def complete(self) -> None:
        """Mark query execution as complete."""
        self.end_time = datetime.now()
        self.status = "completed"

    def fail(self, error_message: str) -> None:
        """Mark query execution as failed.

        Args:
            error_message: Error message describing the failure reason
        """
        self.end_time = datetime.now()
        self.status = "failed"
        self.error = error_message

    def execution_time(self) -> float:
        """Calculate execution time in seconds.

        Returns:
            float: Execution time in seconds, or -1 if not completed
        """
        if not self.end_time:
            return -1
        return (self.end_time - self.start_time).total_seconds()

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the execution context.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def get_metadata(self, key: str) -> Any:
        """Get metadata from the execution context.

        Args:
            key: Metadata key

        Returns:
            Any: Metadata value, or None if not found
        """
        return self.metadata.get(key)


class BaseQuery:
    """Base class for all query representations."""

    def __init__(
        self,
        query_type: str,
        query_string: str,
        parameters: Dict[str, Any] = None,
    ):
        """Initialize a base query.

        Args:
            query_type: Type of query
            query_string: Original query string
            parameters: Query parameters
        """
        self.query_type = query_type
        self.query_string = query_string
        self.parameters = parameters or {}
        self.execution_context: Optional[ExecutionContext] = None

    def validate(self) -> bool:
        """Validate query structure and parameters.

        Returns:
            bool: True if valid, False otherwise
        """
        # Basic validation, should be overridden by subclasses
        return self.query_type is not None and self.query_string is not None

    def to_string(self) -> str:
        """Convert query back to string representation.

        Returns:
            str: String representation of the query
        """
        return self.query_string

    def get_parameter(self, name: str, default: Any = None) -> Any:
        """Get a parameter value.

        Args:
            name: Parameter name
            default: Default value if parameter not found

        Returns:
            Any: Parameter value or default
        """
        return self.parameters.get(name, default)

    def set_execution_context(self, context: ExecutionContext) -> None:
        """Set execution context for this query.

        Args:
            context: Execution context
        """
        self.execution_context = context

    def get_execution_context(self) -> Optional[ExecutionContext]:
        """Get execution context for this query.

        Returns:
            Optional[ExecutionContext]: Execution context if set, None otherwise
        """
        return self.execution_context
