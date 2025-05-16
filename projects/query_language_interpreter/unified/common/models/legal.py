"""Common models for legal discovery query language."""

from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from common.models.base import BaseModel, Category


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


class LegalDocumentType(str, Enum):
    """Types of legal documents."""
    
    EMAIL = "email"
    CONTRACT = "contract"
    MEMO = "memo"
    LETTER = "letter"
    FILING = "filing"
    PLEADING = "pleading"
    DEPOSITION = "deposition"
    TESTIMONY = "testimony"
    EXHIBIT = "exhibit"
    REPORT = "report"
    INVOICE = "invoice"
    OTHER = "other"


class PrivilegeStatus(str, Enum):
    """Privilege status for legal documents."""
    
    NOT_PRIVILEGED = "not_privileged"
    POTENTIALLY_PRIVILEGED = "potentially_privileged"
    PRIVILEGED = "privileged"
    ATTORNEY_CLIENT = "attorney_client"
    WORK_PRODUCT = "work_product"
    OTHER_PRIVILEGE = "other_privilege"
    UNKNOWN = "unknown"


class TimePeriodUnit(str, Enum):
    """Units for time periods."""
    
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"


class TimePeriod(BaseModel):
    """Represents a time period."""
    
    def __init__(
        self,
        amount: int,
        unit: TimePeriodUnit,
        description: str = "",
    ):
        """Initialize a time period.
        
        Args:
            amount: Amount of time
            unit: Unit of time
            description: Description of the time period
        """
        self.amount = amount
        self.unit = unit if isinstance(unit, TimePeriodUnit) else TimePeriodUnit(unit)
        self.description = description
    
    def to_days(self) -> int:
        """Convert time period to days.
        
        Returns:
            int: Number of days
        """
        if self.unit == TimePeriodUnit.DAYS:
            return self.amount
        elif self.unit == TimePeriodUnit.WEEKS:
            return self.amount * 7
        elif self.unit == TimePeriodUnit.MONTHS:
            return self.amount * 30  # Approximation
        elif self.unit == TimePeriodUnit.YEARS:
            return self.amount * 365  # Approximation
        
        return self.amount  # Default to returning the amount
    
    def __str__(self) -> str:
        """String representation of the time period.
        
        Returns:
            str: String representation
        """
        return f"{self.amount} {self.unit.value}"


class LegalTimeframe(BaseModel):
    """Represents a legal timeframe for filtering documents."""
    
    def __init__(
        self,
        name: str,
        description: str = "",
        reference_date: Optional[datetime] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        before_period: Optional[TimePeriod] = None,
        after_period: Optional[TimePeriod] = None,
    ):
        """Initialize a legal timeframe.
        
        Args:
            name: Name of the timeframe
            description: Description of the timeframe
            reference_date: Reference date for relative calculations
            start_date: Explicit start date
            end_date: Explicit end date
            before_period: Time period before reference date
            after_period: Time period after reference date
        """
        self.name = name
        self.description = description
        self.reference_date = reference_date or datetime.now()
        self.start_date = start_date
        self.end_date = end_date
        self.before_period = before_period
        self.after_period = after_period
    
    def calculate_dates(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Calculate start and end dates based on periods and reference date.
        
        Returns:
            Tuple[Optional[datetime], Optional[datetime]]: Calculated start and end dates
        """
        start = self.start_date
        end = self.end_date
        
        # Calculate start date if not explicitly provided
        if not start and self.before_period:
            days = self.before_period.to_days()
            start = self.reference_date - timedelta(days=days)
        
        # Calculate end date if not explicitly provided
        if not end and self.after_period:
            days = self.after_period.to_days()
            end = self.reference_date + timedelta(days=days)
        
        return start, end
    
    def is_date_in_timeframe(self, date: datetime) -> bool:
        """Check if a date is within the timeframe.
        
        Args:
            date: Date to check
            
        Returns:
            bool: True if date is within timeframe, False otherwise
        """
        start, end = self.calculate_dates()
        
        if start and date < start:
            return False
        
        if end and date > end:
            return False
        
        return True


class PrivilegeIndicator(BaseModel):
    """Indicator of potential privilege in documents."""
    
    def __init__(
        self,
        indicator_id: str,
        pattern: str,
        description: str = "",
        weight: float = 1.0,
        category: str = "default",
    ):
        """Initialize a privilege indicator.
        
        Args:
            indicator_id: Unique identifier for the indicator
            pattern: Pattern to match (regex or text)
            description: Description of the indicator
            weight: Weight of the indicator for scoring
            category: Category of the indicator
        """
        self.indicator_id = indicator_id
        self.pattern = pattern
        self.description = description
        self.weight = weight
        self.category = category
    
    def __str__(self) -> str:
        """String representation of the privilege indicator.
        
        Returns:
            str: String representation
        """
        return f"PrivilegeIndicator({self.indicator_id}, weight={self.weight})"


class Attorney(BaseModel):
    """Represents an attorney for privilege detection."""
    
    def __init__(
        self,
        name: str,
        email: Optional[str] = None,
        bar_number: Optional[str] = None,
        firm: Optional[str] = None,
        position: Optional[str] = None,
        practice_areas: List[str] = None,
    ):
        """Initialize an attorney.
        
        Args:
            name: Attorney name
            email: Attorney email
            bar_number: Bar number
            firm: Law firm
            position: Position or title
            practice_areas: Areas of practice
        """
        self.name = name
        self.email = email
        self.bar_number = bar_number
        self.firm = firm
        self.position = position
        self.practice_areas = practice_areas or []
    
    def __str__(self) -> str:
        """String representation of the attorney.
        
        Returns:
            str: String representation
        """
        if self.email:
            return f"{self.name} <{self.email}>"
        return self.name


class ProximityMatch(BaseModel):
    """Represents a proximity match between terms in a document."""
    
    def __init__(
        self,
        terms: List[str],
        positions: List[List[int]],
        distances: List[int],
        document_id: str = "",
        unit: str = "word",
    ):
        """Initialize a proximity match.
        
        Args:
            terms: Terms that matched
            positions: Positions of each term
            distances: Distances between terms
            document_id: Document ID
            unit: Unit of proximity (word, sentence, paragraph)
        """
        self.terms = terms
        self.positions = positions
        self.distances = distances
        self.document_id = document_id
        self.unit = unit
    
    def get_average_distance(self) -> float:
        """Calculate average distance between terms.
        
        Returns:
            float: Average distance
        """
        if not self.distances:
            return 0.0
        
        return sum(self.distances) / len(self.distances)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "terms": self.terms,
            "positions": self.positions,
            "distances": self.distances,
            "document_id": self.document_id,
            "unit": self.unit,
            "average_distance": self.get_average_distance(),
        }