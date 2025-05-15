"""Query models for the legal discovery interpreter."""

from typing import Dict, List, Optional, Any, Union, Set
from enum import Enum, auto
from datetime import datetime, date, timedelta
from pydantic import BaseModel, Field

from common.core.query import BaseQuery, ExecutionContext
from common.core.result import QueryResult as CommonQueryResult


class QueryOperator(str, Enum):
    """Query operators for the legal discovery query language."""
    
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    NEAR = "NEAR"
    WITHIN = "WITHIN"
    CONTAINS = "CONTAINS"
    STARTS_WITH = "STARTS_WITH"
    ENDS_WITH = "ENDS_WITH"
    EQUALS = "EQUALS"
    GREATER_THAN = "GREATER_THAN"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN_EQUALS = "GREATER_THAN_EQUALS"
    LESS_THAN_EQUALS = "LESS_THAN_EQUALS"
    BETWEEN = "BETWEEN"
    IN = "IN"


class DistanceUnit(str, Enum):
    """Units for proximity distance measurement."""
    
    WORDS = "WORDS"
    SENTENCES = "SENTENCES"
    PARAGRAPHS = "PARAGRAPHS"
    SECTIONS = "SECTIONS"
    PAGES = "PAGES"


class QueryType(str, Enum):
    """Types of queries that can be executed."""
    
    FULL_TEXT = "FULL_TEXT"
    METADATA = "METADATA"
    PROXIMITY = "PROXIMITY"
    COMMUNICATION = "COMMUNICATION"
    TEMPORAL = "TEMPORAL"
    PRIVILEGE = "PRIVILEGE"
    COMPOSITE = "COMPOSITE"


class SortOrder(str, Enum):
    """Sort orders for query results."""
    
    ASC = "ASC"
    DESC = "DESC"


class SortField(BaseModel):
    """Field to sort query results by."""
    
    field: str = Field(..., description="Field name to sort by")
    order: SortOrder = Field(default=SortOrder.DESC, description="Sort order")


class QueryClause(BaseModel):
    """Base class for a query clause."""
    
    query_type: QueryType = Field(..., description="Type of query clause")


class FullTextQuery(QueryClause):
    """Full text query for searching document content."""
    
    query_type: QueryType = Field(default=QueryType.FULL_TEXT, description="Type of query clause")
    terms: List[str] = Field(..., description="Search terms")
    operator: QueryOperator = Field(default=QueryOperator.AND, description="Operator for combining terms")
    expand_terms: bool = Field(default=True, description="Whether to expand terms using legal ontology")
    field: Optional[str] = Field(None, description="Field to search in (defaults to all)")
    boost: float = Field(default=1.0, description="Relevance boost factor")


class MetadataQuery(QueryClause):
    """Query for document metadata."""
    
    query_type: QueryType = Field(default=QueryType.METADATA, description="Type of query clause")
    field: str = Field(..., description="Metadata field to query")
    operator: QueryOperator = Field(..., description="Comparison operator")
    value: Any = Field(..., description="Value to compare against")
    
    class Config:
        """Pydantic model configuration."""
        
        arbitrary_types_allowed = True  # Allow any type for value


class ProximityQuery(QueryClause):
    """Query for terms in proximity to each other."""
    
    query_type: QueryType = Field(default=QueryType.PROXIMITY, description="Type of query clause")
    terms: List[str] = Field(..., description="Terms to search for")
    distance: int = Field(..., description="Maximum distance between terms")
    unit: DistanceUnit = Field(..., description="Unit of distance measurement")
    ordered: bool = Field(default=False, description="Whether terms must appear in the specified order")
    expand_terms: bool = Field(default=True, description="Whether to expand terms using legal ontology")


class CommunicationQuery(QueryClause):
    """Query for communication patterns."""
    
    query_type: QueryType = Field(default=QueryType.COMMUNICATION, description="Type of query clause")
    participants: List[str] = Field(..., description="Participants in the communication")
    direction: Optional[str] = Field(None, description="Direction of communication (e.g., from, to, between)")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range for the communication")
    thread_analysis: bool = Field(default=False, description="Whether to analyze message threads")
    include_cc: bool = Field(default=True, description="Whether to include CC recipients")
    include_bcc: bool = Field(default=False, description="Whether to include BCC recipients")


class TemporalQuery(QueryClause):
    """Query for temporal information."""
    
    query_type: QueryType = Field(default=QueryType.TEMPORAL, description="Type of query clause")
    date_field: str = Field(..., description="Date field to query")
    operator: QueryOperator = Field(..., description="Comparison operator")
    value: Union[datetime, date, str, Dict[str, Any]] = Field(
        ..., description="Date value or legal timeframe reference"
    )
    timeframe_type: Optional[str] = Field(None, description="Type of legal timeframe if applicable")
    jurisdiction: Optional[str] = Field(None, description="Jurisdiction for the timeframe if applicable")


class PrivilegeQuery(QueryClause):
    """Query for privilege detection."""
    
    query_type: QueryType = Field(default=QueryType.PRIVILEGE, description="Type of query clause")
    privilege_type: Optional[str] = Field(None, description="Type of privilege to detect")
    threshold: float = Field(default=0.5, description="Confidence threshold for privilege detection")
    attorneys: Optional[List[str]] = Field(None, description="List of attorneys to match")
    include_potentially_privileged: bool = Field(default=True, 
                                               description="Whether to include potentially privileged documents")


class CompositeQuery(QueryClause):
    """Composite query combining multiple query clauses."""
    
    query_type: QueryType = Field(default=QueryType.COMPOSITE, description="Type of query clause")
    operator: QueryOperator = Field(..., description="Operator for combining clauses")
    clauses: List[QueryClause] = Field(..., description="Query clauses to combine")


class LegalQueryResult(CommonQueryResult):
    """Result of a legal discovery query execution."""
    
    document_ids: List[str] = Field(default_factory=list, description="Matching document IDs")
    relevance_scores: Optional[Dict[str, float]] = Field(None, description="Relevance scores for documents")
    privilege_status: Optional[Dict[str, str]] = Field(None, description="Privilege status for documents")
    executed_at: datetime = Field(default_factory=datetime.now, description="When the query was executed")
    
    pagination: Optional[Dict[str, Any]] = Field(None, description="Pagination information")
    aggregations: Optional[Dict[str, Any]] = Field(None, description="Aggregation results")
    facets: Optional[Dict[str, Any]] = Field(None, description="Facet results")


class LegalDiscoveryQuery(BaseQuery):
    """Main query model for the legal discovery interpreter."""
    
    clauses: List[QueryClause] = Field(..., description="Query clauses")
    sort: Optional[List[SortField]] = Field(None, description="Sort specifications")
    limit: Optional[int] = Field(None, description="Maximum number of results to return")
    offset: Optional[int] = Field(None, description="Offset for pagination")
    aggregations: Optional[Dict[str, Any]] = Field(None, description="Aggregation specifications")
    facets: Optional[List[str]] = Field(None, description="Facet specifications")
    
    highlight: bool = Field(default=False, description="Whether to highlight matching terms")
    expand_terms: bool = Field(default=True, description="Whether to expand terms using legal ontology")
    include_privileged: bool = Field(default=False, description="Whether to include privileged documents")

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
        **kwargs
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
            parameters=parameters
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
                terms_str = f" {clause.operator.value} ".join([f"'{term}'" for term in clause.terms])
                clause_strs.append(f"CONTAINS({clause.field or 'content'}, {terms_str})")
            elif isinstance(clause, MetadataQuery):
                clause_strs.append(f"{clause.field} {clause.operator.value} '{clause.value}'")
            elif isinstance(clause, ProximityQuery):
                terms_str = ", ".join([f"'{term}'" for term in clause.terms])
                clause_strs.append(
                    f"NEAR({terms_str}, {clause.distance}, '{clause.unit.value}', ordered={clause.ordered})"
                )
            elif isinstance(clause, TemporalQuery):
                if isinstance(clause.value, dict):
                    value_str = f"TIMEFRAME('{clause.timeframe_type}', '{clause.jurisdiction}')"
                else:
                    value_str = f"'{clause.value}'"
                clause_strs.append(f"{clause.date_field} {clause.operator.value} {value_str}")
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