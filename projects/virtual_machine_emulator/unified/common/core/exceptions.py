"""
Common exception types for virtual machine emulators.

This module provides a shared set of exceptions that can be used by both
the security-focused and parallel computing-focused VM implementations.
"""

from typing import Dict, Any, Optional


class VMException(Exception):
    """Base exception for all VM-related errors."""
    pass


class MemoryException(VMException):
    """Base exception for memory-related errors."""
    
    def __init__(
        self, 
        message: str, 
        address: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.address = address
        self.context = context or {}


class SegmentationFault(MemoryException):
    """Raised when memory access is outside allocated segments."""
    pass


class ProtectionFault(MemoryException):
    """Raised when memory access violates protection settings."""
    
    def __init__(
        self, 
        message: str, 
        address: Optional[int] = None,
        required_permission: Optional[str] = None,
        current_permission: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, address, context)
        self.required_permission = required_permission
        self.current_permission = current_permission


class InvalidAddressException(MemoryException):
    """Raised when accessing an invalid memory address."""
    pass


class ProcessorException(VMException):
    """Base exception for processor-related errors."""
    pass


class InvalidInstructionException(ProcessorException):
    """Raised when attempting to execute an invalid instruction."""
    
    def __init__(
        self, 
        message: str, 
        opcode: Optional[int] = None,
        pc: Optional[int] = None
    ):
        super().__init__(message)
        self.opcode = opcode
        self.pc = pc


class PrivilegeViolationException(ProcessorException):
    """Raised when an operation requires higher privilege level."""
    
    def __init__(
        self, 
        message: str, 
        required_level: Optional[str] = None,
        current_level: Optional[str] = None
    ):
        super().__init__(message)
        self.required_level = required_level
        self.current_level = current_level


class SynchronizationException(VMException):
    """Base exception for synchronization-related errors."""
    pass


class DeadlockException(SynchronizationException):
    """Raised when deadlock is detected."""
    pass


class RaceConditionException(VMException):
    """Raised when a race condition is detected."""
    
    def __init__(
        self, 
        message: str, 
        address: Optional[int] = None,
        threads: Optional[list] = None
    ):
        super().__init__(message)
        self.address = address
        self.threads = threads or []


class VMConfigurationException(VMException):
    """Raised when VM is configured incorrectly."""
    pass


class ExecutionLimitException(VMException):
    """Raised when execution limits are exceeded."""
    pass