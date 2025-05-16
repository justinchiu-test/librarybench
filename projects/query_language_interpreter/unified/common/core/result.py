"""Result models and formatters for query language interpreters."""

from typing import Any, Dict, List, Optional, Set, Union
from datetime import datetime

from common.core.query import BaseQuery


class QueryResult:
    """Result of a query execution."""

    def __init__(
        self,
        query: BaseQuery,
        data: Union[List[Dict[str, Any]], List[Any]] = None,
        success: bool = True,
        error: str = None,
        metadata: Dict[str, Any] = None,
    ):
        """Initialize a query result.

        Args:
            query: Query that produced this result
            data: Result data
            success: Whether the query was successful
            error: Error message if query failed
            metadata: Additional metadata
        """
        self.query = query
        self.data = data or []
        self.success = success
        self.error = error
        self.metadata = metadata or {}
        
        # Extract execution time if available
        self.execution_time = -1
        context = query.get_execution_context()
        if context:
            self.execution_time = context.execution_time()
            self.metadata.update(context.metadata)

    def row_count(self) -> int:
        """Get the number of rows in the result.

        Returns:
            int: Number of rows
        """
        return len(self.data)

    def is_empty(self) -> bool:
        """Check if the result is empty.

        Returns:
            bool: True if empty, False otherwise
        """
        return len(self.data) == 0

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Any: Metadata value or default
        """
        return self.metadata.get(key, default)

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the result.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "success": self.success,
            "error": self.error,
            "row_count": self.row_count(),
            "execution_time": self.execution_time,
            "data": self.data,
            "metadata": self.metadata,
        }


class LegalQueryResult(QueryResult):
    """Result of a legal discovery query execution."""
    
    def __init__(
        self,
        query: BaseQuery,
        data: Union[List[Dict[str, Any]], List[Any]] = None,
        success: bool = True,
        error: str = None,
        metadata: Dict[str, Any] = None,
        document_ids: List[str] = None,
        relevance_scores: Dict[str, float] = None,
        privilege_info: Dict[str, Any] = None,
    ):
        """Initialize a legal query result.

        Args:
            query: Query that produced this result
            data: Result data
            success: Whether the query was successful
            error: Error message if query failed
            metadata: Additional metadata
            document_ids: IDs of matching documents
            relevance_scores: Relevance scores for documents
            privilege_info: Privilege information for documents
        """
        # Initialize base result
        super().__init__(
            query=query,
            data=data,
            success=success,
            error=error,
            metadata=metadata or {},
        )
        
        # Add legal-specific metadata
        if document_ids:
            self.metadata["document_ids"] = document_ids
        
        if relevance_scores:
            self.metadata["relevance_scores"] = relevance_scores
        
        if privilege_info:
            self.metadata["privilege_info"] = privilege_info
    
    def get_document_ids(self) -> List[str]:
        """Get IDs of matching documents.

        Returns:
            List[str]: Document IDs
        """
        return self.metadata.get("document_ids", [])
    
    def get_relevance_score(self, doc_id: str) -> float:
        """Get relevance score for a document.

        Args:
            doc_id: Document ID

        Returns:
            float: Relevance score, or 0.0 if not found
        """
        scores = self.metadata.get("relevance_scores", {})
        return scores.get(doc_id, 0.0)
    
    def get_privilege_status(self, doc_id: str) -> str:
        """Get privilege status for a document.

        Args:
            doc_id: Document ID

        Returns:
            str: Privilege status, or "unknown" if not found
        """
        privilege_info = self.metadata.get("privilege_info", {})
        doc_info = privilege_info.get(doc_id, {})
        return doc_info.get("status", "unknown")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        result = super().to_dict()
        
        # Add legal-specific fields
        result["document_count"] = len(self.get_document_ids())
        
        return result


class ResultFormatter:
    """Formatter for query results."""

    @staticmethod
    def format_as_dict(result: QueryResult) -> Dict[str, Any]:
        """Format result as dictionary.

        Args:
            result: Query result to format

        Returns:
            Dict[str, Any]: Formatted result
        """
        return result.to_dict()

    @staticmethod
    def format_as_json(result: QueryResult) -> str:
        """Format result as JSON string.

        Args:
            result: Query result to format

        Returns:
            str: JSON-formatted result
        """
        import json
        return json.dumps(result.to_dict(), default=str)

    @staticmethod
    def format_as_table(result: QueryResult) -> str:
        """Format result as ASCII table.

        Args:
            result: Query result to format

        Returns:
            str: Table-formatted result
        """
        if not result.data or not isinstance(result.data[0], dict):
            return "No data or invalid format for table display"

        # Get all column names
        columns = list(result.data[0].keys())
        
        # Calculate column widths
        col_widths = {col: len(col) for col in columns}
        for row in result.data:
            for col in columns:
                width = len(str(row.get(col, "")))
                col_widths[col] = max(col_widths[col], width)
        
        # Build header
        header = " | ".join(
            col.ljust(col_widths[col]) for col in columns
        )
        separator = "-+-".join(
            "-" * col_widths[col] for col in columns
        )
        
        # Build rows
        rows = []
        for row in result.data:
            row_str = " | ".join(
                str(row.get(col, "")).ljust(col_widths[col]) for col in columns
            )
            rows.append(row_str)
        
        # Combine all parts
        return "\n".join([header, separator] + rows)