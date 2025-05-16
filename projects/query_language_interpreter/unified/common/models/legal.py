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


class PrivilegeType(str, Enum):
    """Types of legal privilege."""

    ATTORNEY_CLIENT = "attorney_client"
    WORK_PRODUCT = "work_product"
    ATTORNEY_WORK_PRODUCT = "attorney_work_product"
    COMMON_INTEREST = "common_interest"
    JOINT_DEFENSE = "joint_defense"
    SETTLEMENT_NEGOTIATION = "settlement_negotiation"
    SELF_CRITICAL_ANALYSIS = "self_critical_analysis"
    TRADE_SECRET = "trade_secret"
    EXECUTIVE = "executive"
    OTHER = "other"


class PrivilegeIndicatorCategory(str, Enum):
    """Categories of privilege indicators."""

    HEADER = "header"
    FOOTER = "footer"
    SUBJECT_LINE = "subject_line"
    DOCUMENT_TYPE = "document_type"
    PARTICIPANT = "participant"
    CONTENT = "content"
    METADATA = "metadata"
    FORMATTING = "formatting"
    CONTEXTUAL = "contextual"


class PrivilegeStatus(str, Enum):
    """Privilege status for legal documents."""

    NOT_PRIVILEGED = "not_privileged"
    POTENTIALLY_PRIVILEGED = "potentially_privileged"
    PRIVILEGED = "privileged"
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
        indicator_type: Union[PrivilegeType, str] = PrivilegeType.ATTORNEY_CLIENT,
        indicator_category: Union[
            PrivilegeIndicatorCategory, str
        ] = PrivilegeIndicatorCategory.CONTENT,
        case_sensitive: bool = False,
        exact_match: bool = False,
    ):
        """Initialize a privilege indicator.

        Args:
            indicator_id: Unique identifier for the indicator
            pattern: Pattern to match (regex or text)
            description: Description of the indicator
            weight: Weight of the indicator for scoring
            indicator_type: Type of privilege the indicator suggests
            indicator_category: Category of the indicator
            case_sensitive: Whether the pattern is case sensitive
            exact_match: Whether the pattern requires an exact match
        """
        self.indicator_id = indicator_id
        self.pattern = pattern
        self.description = description
        self.weight = weight

        # Handle indicator_type
        if isinstance(indicator_type, PrivilegeType):
            self.indicator_type = indicator_type
        else:
            try:
                self.indicator_type = PrivilegeType(indicator_type)
            except (ValueError, TypeError):
                self.indicator_type = PrivilegeType.OTHER

        # Handle indicator_category
        if isinstance(indicator_category, PrivilegeIndicatorCategory):
            self.indicator_category = indicator_category
        else:
            try:
                self.indicator_category = PrivilegeIndicatorCategory(indicator_category)
            except (ValueError, TypeError):
                self.indicator_category = PrivilegeIndicatorCategory.CONTENT

        self.case_sensitive = case_sensitive
        self.exact_match = exact_match

    def __str__(self) -> str:
        """String representation of the privilege indicator.

        Returns:
            str: String representation
        """
        return f"PrivilegeIndicator({self.indicator_id}, type={self.indicator_type.value}, weight={self.weight})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "indicator_id": self.indicator_id,
            "pattern": self.pattern,
            "description": self.description,
            "weight": self.weight,
            "indicator_type": self.indicator_type.value,
            "indicator_category": self.indicator_category.value,
            "case_sensitive": self.case_sensitive,
            "exact_match": self.exact_match,
        }


class Attorney(BaseModel):
    """Represents an attorney for privilege detection."""

    def __init__(
        self,
        attorney_id: str,
        name: str,
        email: Optional[str] = None,
        organization: Optional[str] = None,
        bar_number: Optional[str] = None,
        role: Optional[str] = None,
        practice_areas: Optional[List[str]] = None,
        is_internal: bool = False,
    ):
        """Initialize an attorney.

        Args:
            attorney_id: Unique identifier for the attorney
            name: Attorney name
            email: Attorney email
            organization: Law firm or organization
            bar_number: Bar number
            role: Role or title
            practice_areas: Areas of practice
            is_internal: Whether the attorney is internal to the organization
        """
        self.attorney_id = attorney_id
        self.name = name
        self.email = email
        self.organization = organization
        self.bar_number = bar_number
        self.role = role
        self.practice_areas = practice_areas or []
        self.is_internal = is_internal

    def __str__(self) -> str:
        """String representation of the attorney.

        Returns:
            str: String representation
        """
        if self.email:
            return f"{self.name} <{self.email}>"
        return self.name

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "attorney_id": self.attorney_id,
            "name": self.name,
            "email": self.email,
            "organization": self.organization,
            "bar_number": self.bar_number,
            "role": self.role,
            "practice_areas": self.practice_areas,
            "is_internal": self.is_internal,
        }


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


class PrivilegeDetectionResult(BaseModel):
    """Result of privilege detection on a document."""

    def __init__(
        self,
        document_id: str,
        status: PrivilegeStatus,
        confidence: float,
        privilege_types: List[Union[PrivilegeType, str]] = None,
        detected_indicators: Dict[str, float] = None,
        attorneys_involved: List[str] = None,
        notes: Optional[str] = None,
    ):
        """Initialize a privilege detection result.

        Args:
            document_id: ID of the document
            status: Privilege status of the document
            confidence: Confidence score (0.0 to 1.0)
            privilege_types: Types of privilege detected
            detected_indicators: Detected indicators and their scores
            attorneys_involved: Attorneys involved in the document
            notes: Additional notes
        """
        self.document_id = document_id

        # Handle status
        if isinstance(status, PrivilegeStatus):
            self.status = status
        else:
            try:
                self.status = PrivilegeStatus(status)
            except (ValueError, TypeError):
                self.status = PrivilegeStatus.UNKNOWN

        self.confidence = min(1.0, max(0.0, confidence))
        self.privilege_types = []

        # Handle privilege types
        if privilege_types:
            for p_type in privilege_types:
                if isinstance(p_type, PrivilegeType):
                    self.privilege_types.append(p_type)
                else:
                    try:
                        self.privilege_types.append(PrivilegeType(p_type))
                    except (ValueError, TypeError):
                        self.privilege_types.append(PrivilegeType.OTHER)

        self.detected_indicators = detected_indicators or {}
        self.attorneys_involved = attorneys_involved or []
        self.notes = notes

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "document_id": self.document_id,
            "status": self.status.value,
            "confidence": self.confidence,
            "privilege_types": [pt.value for pt in self.privilege_types],
            "detected_indicators": self.detected_indicators,
            "attorneys_involved": self.attorneys_involved,
            "notes": self.notes,
        }


class PrivilegeLog(BaseModel):
    """Log of privilege determinations."""

    def __init__(self):
        """Initialize an empty privilege log."""
        self.entries: Dict[str, PrivilegeDetectionResult] = {}

    def add_entry(self, result: PrivilegeDetectionResult) -> None:
        """Add an entry to the privilege log.

        Args:
            result: Privilege detection result to add
        """
        self.entries[result.document_id] = result

    def get_entry(self, document_id: str) -> Optional[PrivilegeDetectionResult]:
        """Get an entry from the privilege log.

        Args:
            document_id: ID of the document to get entry for

        Returns:
            The privilege detection result, or None if not found
        """
        return self.entries.get(document_id)

    def get_privileged_documents(self) -> List[str]:
        """Get IDs of privileged documents.

        Returns:
            List of privileged document IDs
        """
        return [
            doc_id
            for doc_id, result in self.entries.items()
            if result.status == PrivilegeStatus.PRIVILEGED
        ]

    def get_potentially_privileged_documents(self) -> List[str]:
        """Get IDs of potentially privileged documents.

        Returns:
            List of potentially privileged document IDs
        """
        return [
            doc_id
            for doc_id, result in self.entries.items()
            if result.status == PrivilegeStatus.POTENTIALLY_PRIVILEGED
        ]

    def count_entries(self) -> Dict[str, int]:
        """Count entries by privilege status.

        Returns:
            Dictionary mapping status to count
        """
        counts = {status.value: 0 for status in PrivilegeStatus}

        for result in self.entries.values():
            counts[result.status.value] += 1

        counts["total"] = len(self.entries)

        return counts
