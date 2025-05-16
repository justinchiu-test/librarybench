"""Common query clause models for legal discovery."""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from pydantic import BaseModel, Field

from common.models.legal import QueryOperator, DistanceUnit, QueryType


class QueryClause(BaseModel):
    """Base class for a query clause."""
    
    query_type: QueryType = Field(..., description="Type of query clause")


class FullTextQuery(QueryClause):
    """Full text query for searching document content."""
    
    query_type: QueryType = Field(default=QueryType.FULL_TEXT, description="Type of query clause")
    terms: List[str] = Field(..., description="Search terms")
    operator: QueryOperator = Field(default=QueryOperator.AND, description="Operator for combining terms")
    expand_terms: bool = Field(default=True, description="Whether to expand terms using ontology")
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
    expand_terms: bool = Field(default=True, description="Whether to expand terms using ontology")


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
        ..., description="Date value or timeframe reference"
    )
    timeframe_type: Optional[str] = Field(None, description="Type of timeframe if applicable")
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