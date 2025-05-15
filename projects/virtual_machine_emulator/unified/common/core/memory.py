"""
Memory system for virtual machine emulators.

This module provides a common memory system implementation that can be
used by both the security-focused and parallel computing-focused VM implementations.
"""

from enum import Enum, Flag, auto
from typing import Dict, List, Optional, Set, Tuple, Any, Protocol
import time

from common.core.exceptions import (
    MemoryException, SegmentationFault, ProtectionFault, InvalidAddressException
)


class MemoryAccessType(Enum):
    """Types of memory access operations."""
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()
    READ_MODIFY_WRITE = auto()  # For atomic operations like CAS


class MemoryPermission(Flag):
    """Memory access permissions flags."""
    NONE = 0
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()
    READ_WRITE = READ | WRITE
    READ_EXECUTE = READ | EXECUTE
    WRITE_EXECUTE = WRITE | EXECUTE
    READ_WRITE_EXECUTE = READ | WRITE | EXECUTE


class MemoryProtectionLevel(Enum):
    """Protection enforcement levels for memory operations."""
    NONE = 0        # No protection, all operations permitted
    MINIMAL = 1     # Basic boundary checking
    STANDARD = 2    # Permission enforcement without additional protections
    ENHANCED = 3    # Permission checks plus basic integrity protections
    MAXIMUM = 4     # All protections enabled with strict enforcement
    
    def __lt__(self, other):
        if isinstance(other, MemoryProtectionLevel):
            return self.value < other.value
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, MemoryProtectionLevel):
            return self.value > other.value
        return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, MemoryProtectionLevel):
            return self.value <= other.value
        return NotImplemented
    
    def __ge__(self, other):
        if isinstance(other, MemoryProtectionLevel):
            return self.value >= other.value
        return NotImplemented


class MemoryAccess:
    """Record of a memory access operation."""
    
    def __init__(
        self,
        address: int,
        access_type: MemoryAccessType,
        processor_id: Optional[int] = None,
        thread_id: Optional[str] = None,
        timestamp: Optional[int] = None,
        value: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a memory access record.
        
        Args:
            address: Memory address accessed
            access_type: Type of access (read, write, etc.)
            processor_id: ID of the processor performing the access
            thread_id: ID of the thread performing the access
            timestamp: Timestamp of the access
            value: Value written (for write operations)
            context: Additional context for the access
        """
        self.address = address
        self.access_type = access_type
        self.processor_id = processor_id
        self.thread_id = thread_id
        self.timestamp = timestamp or int(time.time() * 1000)  # Use current time if not provided
        self.value = value
        self.context = context or {}
    
    def __str__(self) -> str:
        """Return a string representation of the memory access."""
        action = self.access_type.name
        proc_info = f"P{self.processor_id}" if self.processor_id is not None else ""
        thread_info = f"T{self.thread_id}" if self.thread_id is not None else ""
        value_info = f" value={self.value}" if self.value is not None else ""
        return f"[{self.timestamp}] {proc_info} {thread_info} {action} addr=0x{self.address:08x}{value_info}"


class MemorySegment:
    """A contiguous segment of memory with specific attributes."""
    
    def __init__(
        self,
        base_address: int,
        size: int,
        permission: MemoryPermission = MemoryPermission.READ_WRITE,
        name: str = "unnamed"
    ):
        """
        Initialize a memory segment.
        
        Args:
            base_address: Starting address of the segment
            size: Size of the segment in bytes/words
            permission: Access permissions for the segment
            name: Name of the segment for identification
        """
        self.base_address = base_address
        self.size = size
        self.end_address = base_address + size - 1
        self.permission = permission
        self.name = name
        self.data = bytearray(size)
    
    def contains_address(self, address: int) -> bool:
        """Check if the segment contains the given address."""
        return self.base_address <= address <= self.end_address
    
    def check_permission(self, address: int, required_permission: MemoryPermission) -> bool:
        """Check if the segment has the required permission for the address."""
        if not self.contains_address(address):
            return False
        return (self.permission & required_permission) == required_permission
    
    def relative_address(self, address: int) -> int:
        """Convert an absolute address to a relative offset in the segment."""
        if not self.contains_address(address):
            raise ValueError(f"Address 0x{address:08x} not in segment {self.name}")
        return address - self.base_address


class MemoryProtection:
    """Configuration for memory protection mechanisms."""
    
    def __init__(
        self,
        level: MemoryProtectionLevel = MemoryProtectionLevel.STANDARD,
        dep_enabled: bool = True,
        aslr_enabled: bool = False,
        stack_canaries: bool = False,
        shadow_memory: bool = False
    ):
        """
        Initialize memory protection settings.
        
        Args:
            level: Protection enforcement level
            dep_enabled: Whether Data Execution Prevention is enabled
            aslr_enabled: Whether Address Space Layout Randomization is enabled
            stack_canaries: Whether stack canaries are used
            shadow_memory: Whether shadow memory is used for integrity checking
        """
        self.level = level
        self.dep_enabled = dep_enabled
        self.aslr_enabled = aslr_enabled
        self.stack_canaries = stack_canaries
        self.shadow_memory = shadow_memory
    
    def get_description(self) -> Dict[str, Any]:
        """Get a description of the protection settings."""
        return {
            "level": self.level.name,
            "dep_enabled": self.dep_enabled,
            "aslr_enabled": self.aslr_enabled,
            "stack_canaries": self.stack_canaries,
            "shadow_memory": self.shadow_memory
        }


class MemorySystem:
    """
    Base memory system for virtual machine emulators.
    
    This implementation provides core memory operations with customizable
    protection levels and access tracking.
    """
    
    def __init__(
        self,
        size: int = 2**16,
        protection_level: MemoryProtectionLevel = MemoryProtectionLevel.STANDARD,
        enable_access_logging: bool = True
    ):
        """
        Initialize the memory system.
        
        Args:
            size: Size of memory in words/bytes
            protection_level: Level of memory protection enforcement
            enable_access_logging: Whether to log memory accesses
        """
        self.size = size
        self.memory = [0] * size  # Raw memory array
        self.protection_level = protection_level
        self.enable_access_logging = enable_access_logging
        self.access_log: List[MemoryAccess] = []
        self.segments: List[MemorySegment] = []
        self.protection_events: List[Dict[str, Any]] = []
    
    def add_segment(self, segment: MemorySegment) -> MemorySegment:
        """
        Add a memory segment to the memory system.
        
        Args:
            segment: The memory segment to add
            
        Returns:
            The added segment
        """
        # Check for overlapping segments
        for existing in self.segments:
            if (segment.base_address <= existing.end_address and 
                existing.base_address <= segment.end_address):
                raise MemoryException(
                    f"Segment {segment.name} overlaps with existing segment {existing.name}"
                )
        
        self.segments.append(segment)
        return segment
    
    def find_segment(self, address: int) -> Optional[MemorySegment]:
        """
        Find the memory segment containing the given address.
        
        Args:
            address: The address to look for
            
        Returns:
            The segment containing the address, or None if not found
        """
        for segment in self.segments:
            if segment.contains_address(address):
                return segment
        return None
    
    def check_address(self, address: int) -> bool:
        """
        Check if an address is valid (within memory bounds).
        
        Args:
            address: The address to check
            
        Returns:
            True if the address is valid, False otherwise
        """
        return 0 <= address < self.size
    
    def _log_access(self, access: MemoryAccess) -> None:
        """
        Log a memory access if logging is enabled.
        
        Args:
            access: The memory access to log
        """
        if self.enable_access_logging:
            self.access_log.append(access)
    
    def _record_protection_event(
        self,
        address: int,
        access_type: MemoryAccessType,
        current_permission: MemoryPermission,
        required_permission: MemoryPermission,
        context: Dict[str, Any]
    ) -> None:
        """
        Record a protection violation event.
        
        Args:
            address: The memory address
            access_type: The type of access attempted
            current_permission: The current permission of the memory
            required_permission: The permission required for the access
            context: Additional context for the event
        """
        event = {
            "address": address,
            "access_type": access_type.name,
            "current_permission": current_permission.name,
            "required_permission": required_permission.name,
            "timestamp": int(time.time() * 1000),
            "context": context.copy() if context else {}
        }
        self.protection_events.append(event)
    
    def read(
        self,
        address: int,
        processor_id: Optional[int] = None,
        thread_id: Optional[str] = None,
        timestamp: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Read a value from memory.
        
        Args:
            address: The memory address to read from
            processor_id: ID of the processor performing the read
            thread_id: ID of the thread performing the read
            timestamp: Timestamp of the read operation
            context: Additional context for the read
            
        Returns:
            The value read from memory
            
        Raises:
            InvalidAddressException: If address is outside memory bounds
            SegmentationFault: If address is not in any segment
            ProtectionFault: If the read violates memory protection
        """
        # Basic bounds checking
        if not self.check_address(address):
            raise InvalidAddressException(f"Memory address out of bounds: 0x{address:08x}")
        
        # Protection checking if segments are defined
        if self.segments and self.protection_level != MemoryProtectionLevel.NONE:
            segment = self.find_segment(address)
            if segment is None:
                if self.protection_level >= MemoryProtectionLevel.MINIMAL:
                    self._record_protection_event(
                        address, MemoryAccessType.READ, 
                        MemoryPermission.NONE, MemoryPermission.READ, context or {}
                    )
                    raise SegmentationFault(
                        f"Address 0x{address:08x} not in any memory segment",
                        address, context
                    )
            elif not segment.check_permission(address, MemoryPermission.READ):
                if self.protection_level >= MemoryProtectionLevel.STANDARD:
                    self._record_protection_event(
                        address, MemoryAccessType.READ, 
                        segment.permission, MemoryPermission.READ, context or {}
                    )
                    raise ProtectionFault(
                        f"Read permission denied at address 0x{address:08x}",
                        address, "READ", segment.permission.name, context
                    )
        
        # Perform the read
        value = self.memory[address]
        
        # Log the access
        access = MemoryAccess(
            address=address,
            access_type=MemoryAccessType.READ,
            processor_id=processor_id,
            thread_id=thread_id,
            timestamp=timestamp,
            context=context
        )
        self._log_access(access)
        
        return value
    
    def write(
        self,
        address: int,
        value: int,
        processor_id: Optional[int] = None,
        thread_id: Optional[str] = None,
        timestamp: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Write a value to memory.
        
        Args:
            address: The memory address to write to
            value: The value to write
            processor_id: ID of the processor performing the write
            thread_id: ID of the thread performing the write
            timestamp: Timestamp of the write operation
            context: Additional context for the write
            
        Raises:
            InvalidAddressException: If address is outside memory bounds
            SegmentationFault: If address is not in any segment
            ProtectionFault: If the write violates memory protection
        """
        # Basic bounds checking
        if not self.check_address(address):
            raise InvalidAddressException(f"Memory address out of bounds: 0x{address:08x}")
        
        # Protection checking if segments are defined
        if self.segments and self.protection_level != MemoryProtectionLevel.NONE:
            segment = self.find_segment(address)
            if segment is None:
                if self.protection_level >= MemoryProtectionLevel.MINIMAL:
                    self._record_protection_event(
                        address, MemoryAccessType.WRITE, 
                        MemoryPermission.NONE, MemoryPermission.WRITE, context or {}
                    )
                    raise SegmentationFault(
                        f"Address 0x{address:08x} not in any memory segment",
                        address, context
                    )
            elif not segment.check_permission(address, MemoryPermission.WRITE):
                if self.protection_level >= MemoryProtectionLevel.STANDARD:
                    self._record_protection_event(
                        address, MemoryAccessType.WRITE, 
                        segment.permission, MemoryPermission.WRITE, context or {}
                    )
                    raise ProtectionFault(
                        f"Write permission denied at address 0x{address:08x}",
                        address, "WRITE", segment.permission.name, context
                    )
        
        # Perform the write
        self.memory[address] = value
        
        # Log the access
        access = MemoryAccess(
            address=address,
            access_type=MemoryAccessType.WRITE,
            processor_id=processor_id,
            thread_id=thread_id,
            timestamp=timestamp,
            value=value,
            context=context
        )
        self._log_access(access)
    
    def execute(
        self,
        address: int,
        processor_id: Optional[int] = None,
        thread_id: Optional[str] = None,
        timestamp: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Fetch and execute an instruction from memory.
        
        Args:
            address: The memory address to execute from
            processor_id: ID of the processor performing the execution
            thread_id: ID of the thread performing the execution
            timestamp: Timestamp of the execution
            context: Additional context for the execution
            
        Returns:
            The instruction value from memory
            
        Raises:
            InvalidAddressException: If address is outside memory bounds
            SegmentationFault: If address is not in any segment
            ProtectionFault: If execution violates memory protection
        """
        # Basic bounds checking
        if not self.check_address(address):
            raise InvalidAddressException(f"Memory address out of bounds: 0x{address:08x}")
        
        # Protection checking if segments are defined and DEP is enabled
        if self.segments and self.protection_level != MemoryProtectionLevel.NONE:
            segment = self.find_segment(address)
            if segment is None:
                if self.protection_level >= MemoryProtectionLevel.MINIMAL:
                    self._record_protection_event(
                        address, MemoryAccessType.EXECUTE, 
                        MemoryPermission.NONE, MemoryPermission.EXECUTE, context or {}
                    )
                    raise SegmentationFault(
                        f"Address 0x{address:08x} not in any memory segment",
                        address, context
                    )
            elif not segment.check_permission(address, MemoryPermission.EXECUTE):
                if self.protection_level >= MemoryProtectionLevel.STANDARD:
                    self._record_protection_event(
                        address, MemoryAccessType.EXECUTE, 
                        segment.permission, MemoryPermission.EXECUTE, context or {}
                    )
                    raise ProtectionFault(
                        f"Execute permission denied at address 0x{address:08x}",
                        address, "EXECUTE", segment.permission.name, context
                    )
        
        # Perform the read for execution
        value = self.memory[address]
        
        # Log the access
        access = MemoryAccess(
            address=address,
            access_type=MemoryAccessType.EXECUTE,
            processor_id=processor_id,
            thread_id=thread_id,
            timestamp=timestamp,
            context=context
        )
        self._log_access(access)
        
        return value
    
    def compare_and_swap(
        self,
        address: int,
        expected: int,
        new_value: int,
        processor_id: Optional[int] = None,
        thread_id: Optional[str] = None,
        timestamp: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Perform an atomic compare-and-swap operation.
        
        Args:
            address: The memory address to operate on
            expected: The expected current value
            new_value: The new value to set if expected matches current
            processor_id: ID of the processor performing the operation
            thread_id: ID of the thread performing the operation
            timestamp: Timestamp of the operation
            context: Additional context for the operation
            
        Returns:
            True if the swap was performed, False otherwise
            
        Raises:
            InvalidAddressException: If address is outside memory bounds
            SegmentationFault: If address is not in any segment
            ProtectionFault: If the operation violates memory protection
        """
        # Basic bounds checking
        if not self.check_address(address):
            raise InvalidAddressException(f"Memory address out of bounds: 0x{address:08x}")
        
        # Protection checking if segments are defined
        if self.segments and self.protection_level != MemoryProtectionLevel.NONE:
            segment = self.find_segment(address)
            if segment is None:
                if self.protection_level >= MemoryProtectionLevel.MINIMAL:
                    self._record_protection_event(
                        address, MemoryAccessType.READ_MODIFY_WRITE, 
                        MemoryPermission.NONE, MemoryPermission.READ_WRITE, context or {}
                    )
                    raise SegmentationFault(
                        f"Address 0x{address:08x} not in any memory segment",
                        address, context
                    )
            elif not segment.check_permission(address, MemoryPermission.READ_WRITE):
                if self.protection_level >= MemoryProtectionLevel.STANDARD:
                    self._record_protection_event(
                        address, MemoryAccessType.READ_MODIFY_WRITE, 
                        segment.permission, MemoryPermission.READ_WRITE, context or {}
                    )
                    raise ProtectionFault(
                        f"Read-modify-write permission denied at address 0x{address:08x}",
                        address, "READ_WRITE", segment.permission.name, context
                    )
        
        # Perform the CAS operation atomically
        current = self.memory[address]
        success = current == expected
        
        if success:
            self.memory[address] = new_value
        
        # Log the access
        access = MemoryAccess(
            address=address,
            access_type=MemoryAccessType.READ_MODIFY_WRITE,
            processor_id=processor_id,
            thread_id=thread_id,
            timestamp=timestamp,
            value=new_value if success else None,
            context=context
        )
        self._log_access(access)
        
        return success
    
    def get_access_history(
        self,
        address: Optional[int] = None,
        access_type: Optional[MemoryAccessType] = None,
        processor_id: Optional[int] = None,
        thread_id: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[MemoryAccess]:
        """
        Get a filtered history of memory accesses.
        
        Args:
            address: Filter by memory address
            access_type: Filter by access type
            processor_id: Filter by processor ID
            thread_id: Filter by thread ID
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            List of memory access records matching the filters
        """
        result = self.access_log
        
        if address is not None:
            result = [access for access in result if access.address == address]
        
        if access_type is not None:
            result = [access for access in result if access.access_type == access_type]
        
        if processor_id is not None:
            result = [access for access in result if access.processor_id == processor_id]
        
        if thread_id is not None:
            result = [access for access in result if access.thread_id == thread_id]
        
        if start_time is not None:
            result = [access for access in result if access.timestamp >= start_time]
        
        if end_time is not None:
            result = [access for access in result if access.timestamp <= end_time]
        
        return result
    
    def get_protection_events(self) -> List[Dict[str, Any]]:
        """Get all recorded protection events."""
        return self.protection_events
    
    def clear_logs(self) -> None:
        """Clear all access logs and protection events."""
        self.access_log = []
        self.protection_events = []
    
    def get_memory_dump(self, start: int = 0, length: Optional[int] = None) -> List[int]:
        """
        Get a dump of memory contents.
        
        Args:
            start: Starting address
            length: Number of words to include, or None for all remaining
            
        Returns:
            List of memory values
        """
        if not self.check_address(start):
            raise InvalidAddressException(f"Start address out of bounds: 0x{start:08x}")
        
        if length is None:
            length = self.size - start
        
        end = min(start + length, self.size)
        return self.memory[start:end]
    
    def get_memory_map(self) -> List[Dict[str, Any]]:
        """
        Get a description of all memory segments.
        
        Returns:
            List of segment descriptions
        """
        return [
            {
                "name": segment.name,
                "base_address": segment.base_address,
                "end_address": segment.end_address,
                "size": segment.size,
                "permission": segment.permission.name
            }
            for segment in self.segments
        ]
    
    def reset(self) -> None:
        """Reset the memory system to initial state."""
        self.memory = [0] * self.size
        self.access_log = []
        self.protection_events = []
        
        # Clear segment data but keep the segment structure
        for segment in self.segments:
            segment.data = bytearray(segment.size)