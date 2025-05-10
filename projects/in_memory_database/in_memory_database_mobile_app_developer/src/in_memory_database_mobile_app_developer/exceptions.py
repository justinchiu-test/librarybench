"""Exceptions for MobileSyncDB."""


class MobileSyncDBError(Exception):
    """Base exception for all MobileSyncDB errors."""


class TableAlreadyExistsError(MobileSyncDBError):
    """Raised when attempting to create a table that already exists."""


class TableNotFoundError(MobileSyncDBError):
    """Raised when attempting to access a table that does not exist."""


class RecordNotFoundError(MobileSyncDBError):
    """Raised when attempting to access a record that does not exist."""


class SchemaValidationError(MobileSyncDBError):
    """Raised when a record does not conform to the table schema."""


class IndexError(MobileSyncDBError):
    """Raised when there is an error with table indexes."""


class SyncError(MobileSyncDBError):
    """Raised when there is an error during synchronization."""


class ConflictError(MobileSyncDBError):
    """Raised when there is a conflict during synchronization."""


class CompressionError(MobileSyncDBError):
    """Raised when there is an error during compression or decompression."""


class SchemaVersionError(MobileSyncDBError):
    """Raised when there is an error with schema versioning."""


class BatteryModeError(MobileSyncDBError):
    """Raised when there is an error with battery-aware operations."""


class MemoryLimitError(MobileSyncDBError):
    """Raised when the database exceeds its memory limit."""


class NetworkError(MobileSyncDBError):
    """Raised when there is a network-related error."""


class AuthenticationError(MobileSyncDBError):
    """Raised when there is an authentication error."""


class CorruptDataError(MobileSyncDBError):
    """Raised when corrupt data is detected during sync or operations."""