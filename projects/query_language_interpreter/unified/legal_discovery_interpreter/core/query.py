"""Query models for the legal discovery interpreter."""

from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime, date, timedelta
from pydantic import BaseModel, Field

from common.core.query import BaseQuery, ExecutionContext
from common.core.result import QueryResult
from common.models.legal import QueryOperator, DistanceUnit, QueryType, SortOrder
from common.core.legal_clauses import (
    QueryClause,
    FullTextQuery,
    MetadataQuery,
    ProximityQuery,
    CommunicationQuery,
    TemporalQuery,
    PrivilegeQuery,
    CompositeQuery,
)


# Create a base result class that doesn't set execution_time directly
class CommonQueryResult(QueryResult):
    """Base query result that doesn't set execution_time attribute."""

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

        # Extract context metadata if available
        context = query.get_execution_context()
        if context:
            if not "execution_time" in self.metadata:
                self.metadata["execution_time"] = context.execution_time()
            self.metadata.update(context.metadata)


class SortField(BaseModel):
    """Field to sort query results by."""

    field: str = Field(..., description="Field name to sort by")
    order: SortOrder = Field(default=SortOrder.DESC, description="Sort order")


class LegalQueryResult(CommonQueryResult):
    """Result of a legal discovery query execution."""

    # For backward compatibility, add property methods that get data from metadata
    @property
    def query_id(self) -> str:
        """Get query ID from the query."""
        if hasattr(self.query, "query_id"):
            return self.query.query_id
        return None

    @property
    def document_ids(self) -> List[str]:
        """Get document IDs from metadata."""
        return self.metadata.get("document_ids", [])

    @property
    def total_hits(self) -> int:
        """Get total hits from metadata."""
        return self.metadata.get("total_hits", 0)

    @property
    def relevance_scores(self) -> Dict[str, float]:
        """Get relevance scores from metadata."""
        return self.metadata.get("relevance_scores", {})

    @property
    def privilege_status(self) -> Dict[str, str]:
        """Get privilege status from metadata."""
        return self.metadata.get("privilege_status", {})

    @property
    def executed_at(self) -> datetime:
        """Get execution timestamp from metadata."""
        return self.metadata.get("executed_at", datetime.now())

    @property
    def execution_time(self) -> float:
        """Get execution time from metadata."""
        return self.metadata.get(
            "execution_time", self.get_metadata("execution_time", -1)
        )

    @property
    def pagination(self) -> Dict[str, Any]:
        """Get pagination from metadata."""
        return self.metadata.get("pagination", {})

    @property
    def aggregations(self) -> Dict[str, Any]:
        """Get aggregations from metadata."""
        return self.metadata.get("aggregations", {})

    @property
    def facets(self) -> Dict[str, Any]:
        """Get facets from metadata."""
        return self.metadata.get("facets", {})


class LegalDiscoveryQuery(BaseQuery):
    """Main query model for the legal discovery interpreter."""

    clauses: List[QueryClause] = Field(..., description="Query clauses")
    sort: Optional[List[SortField]] = Field(None, description="Sort specifications")
    limit: Optional[int] = Field(
        None, description="Maximum number of results to return"
    )
    offset: Optional[int] = Field(None, description="Offset for pagination")
    aggregations: Optional[Dict[str, Any]] = Field(
        None, description="Aggregation specifications"
    )
    facets: Optional[List[str]] = Field(None, description="Facet specifications")

    highlight: bool = Field(
        default=False, description="Whether to highlight matching terms"
    )
    expand_terms: bool = Field(
        default=True, description="Whether to expand terms using legal ontology"
    )
    include_privileged: bool = Field(
        default=False, description="Whether to include privileged documents"
    )

    class Config:
        """Pydantic model configuration."""

        arbitrary_types_allowed = True

    def __init__(
        self,
        query_id: str,
        clauses: List[QueryClause],
        sort: Optional[List[SortField]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        aggregations: Optional[Dict[str, Any]] = None,
        facets: Optional[List[str]] = None,
        highlight: bool = False,
        expand_terms: bool = True,
        include_privileged: bool = False,
        **kwargs,
    ):
        """Initialize a legal discovery query.

        Args:
            query_id: Unique identifier for the query
            clauses: Query clauses
            sort: Sort specifications
            limit: Maximum number of results to return
            offset: Offset for pagination
            aggregations: Aggregation specifications
            facets: Facet specifications
            highlight: Whether to highlight matching terms
            expand_terms: Whether to expand terms using legal ontology
            include_privileged: Whether to include privileged documents
        """
        # Initialize BaseQuery attributes
        query_string = self._generate_query_string(clauses)
        parameters = {
            "sort": sort,
            "limit": limit,
            "offset": offset,
            "aggregations": aggregations,
            "facets": facets,
            "highlight": highlight,
            "expand_terms": expand_terms,
            "include_privileged": include_privileged,
        }
        super().__init__(
            query_type="LEGAL_DISCOVERY",
            query_string=query_string,
            parameters=parameters,
        )

        # Set LegalDiscoveryQuery specific attributes
        self.query_id = query_id
        self.clauses = clauses
        self.sort = sort
        self.limit = limit
        self.offset = offset
        self.aggregations = aggregations
        self.facets = facets
        self.highlight = highlight
        self.expand_terms = expand_terms
        self.include_privileged = include_privileged

    def _generate_query_string(self, clauses: List[QueryClause]) -> str:
        """Generate a string representation of the query clauses.

        Args:
            clauses: Query clauses

        Returns:
            String representation of the query
        """
        if not clauses:
            return ""

        try:
            return self.to_sql_like()
        except:
            # Fallback for when to_sql_like fails during initialization
            return str(clauses)

    def validate(self) -> bool:
        """Validate query structure and parameters.

        Returns:
            bool: True if valid, False otherwise
        """
        # Basic validation
        if not self.query_id or not self.clauses:
            return False

        # Additional validation could be added here

        return True

    def to_string(self) -> str:
        """Convert query back to string representation.

        Returns:
            str: String representation of the query
        """
        return self.to_sql_like()

    def to_sql_like(self) -> str:
        """Convert the query to a SQL-like string representation.

        Returns:
            SQL-like string representation of the query
        """
        # A simplified implementation for demonstration purposes
        # A full implementation would need to recursively process the query clauses
        clause_strs = []
        for clause in self.clauses:
            if isinstance(clause, FullTextQuery):
                terms_str = f" {clause.operator.value} ".join(
                    [f"'{term}'" for term in clause.terms]
                )
                clause_strs.append(
                    f"CONTAINS({clause.field or 'content'}, {terms_str})"
                )
            elif isinstance(clause, MetadataQuery):
                clause_strs.append(
                    f"{clause.field} {clause.operator.value} '{clause.value}'"
                )
            elif isinstance(clause, ProximityQuery):
                terms_str = ", ".join([f"'{term}'" for term in clause.terms])
                clause_strs.append(
                    f"NEAR({terms_str}, {clause.distance}, '{clause.unit.value}', ordered={clause.ordered})"
                )
            elif isinstance(clause, TemporalQuery):
                if isinstance(clause.value, dict):
                    value_str = (
                        f"TIMEFRAME('{clause.timeframe_type}', '{clause.jurisdiction}')"
                    )
                else:
                    value_str = f"'{clause.value}'"
                clause_strs.append(
                    f"{clause.date_field} {clause.operator.value} {value_str}"
                )
            elif isinstance(clause, PrivilegeQuery):
                clause_strs.append(
                    f"PRIVILEGE_CHECK(type='{clause.privilege_type or 'ANY'}', threshold={clause.threshold})"
                )
            elif isinstance(clause, CommunicationQuery):
                participants_str = ", ".join([f"'{p}'" for p in clause.participants])
                clause_strs.append(
                    f"COMMUNICATION({participants_str}, direction='{clause.direction or 'ANY'}')"
                )

        query_str = " AND ".join(clause_strs)

        if self.sort:
            sort_strs = [f"{sort.field} {sort.order.value}" for sort in self.sort]
            query_str += f" ORDER BY {', '.join(sort_strs)}"

        if self.limit is not None:
            query_str += f" LIMIT {self.limit}"

        if self.offset is not None:
            query_str += f" OFFSET {self.offset}"

        return query_str
