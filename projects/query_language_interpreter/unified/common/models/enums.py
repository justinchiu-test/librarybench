"""Common enumerations for query language interpreters."""

from enum import Enum, auto


class QueryType(str, Enum):
    """Types of queries."""
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SEARCH = "SEARCH"
    ANALYZE = "ANALYZE"
    CUSTOM = "CUSTOM"


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class PatternType(str, Enum):
    """Types of patterns."""
    REGEX = "REGEX"
    KEYWORD = "KEYWORD"
    DICTIONARY = "DICTIONARY"
    SEMANTIC = "SEMANTIC"


class PolicySeverity(str, Enum):
    """Policy violation severity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ExecutionStatus(str, Enum):
    """Query execution status."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class DataCategory(str, Enum):
    """Data categories."""
    PERSONAL = "PERSONAL"
    SENSITIVE = "SENSITIVE"
    CONFIDENTIAL = "CONFIDENTIAL"
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"


class SensitivityLevel(str, Enum):
    """Data sensitivity levels."""
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AccessType(str, Enum):
    """Types of data access."""
    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"
    EXECUTE = "EXECUTE"
    ADMIN = "ADMIN"


class Purpose(str, Enum):
    """Purposes for data access."""
    BUSINESS = "BUSINESS"
    COMPLIANCE = "COMPLIANCE"
    LEGAL = "LEGAL"
    SECURITY = "SECURITY"
    SUPPORT = "SUPPORT"
    MARKETING = "MARKETING"
    ANALYTICS = "ANALYTICS"
    RESEARCH = "RESEARCH"