"""Common models for legal discovery query language."""

from enum import Enum, auto
from typing import Any, Dict, List, Optional, Union


class QueryOperator(str, Enum):
    """Query operators for the query language."""
    
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