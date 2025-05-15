"""
Memory management and protection mechanisms for the secure VM.

This module implements a detailed memory model with various protection mechanisms
including memory permissions, boundary checking, and protection levels.
"""

from __future__ import annotations
import random
import struct
from typing import Dict, List, Optional, Set, Tuple, Union, Any

from common.core.memory import (
    MemorySystem as BaseMemorySystem,
    MemorySegment as BaseMemorySegment,
    MemoryAccessType,
    MemoryPermission,
    MemoryProtectionLevel,
    MemoryAccess
)
from common.core.exceptions import (
    MemoryException, SegmentationFault, ProtectionFault, InvalidAddressException
)
from common.extensions.security.memory_protection import (
    MemoryProtection, MemoryProtectionException, DEPViolationException, StackCanaryException
)


# Re-export common types
MemoryPermission = MemoryPermission
MemoryProtectionLevel = MemoryProtectionLevel
# Re-export MemoryProtection for backward compatibility
MemoryProtection = MemoryProtection


class ProtectionBypassAttempt:
    """Records an attempt to bypass memory protection mechanisms."""
    
    def __init__(
        self,
        address: int,
        access_type: str,
        current_permission: MemoryPermission,
        required_permission: MemoryPermission,
        instruction_pointer: int,
        context: Dict[str, Any],
    ):
        self.address = address
        self.access_type = access_type
        self.current_permission = current_permission
        self.required_permission = required_permission
        self.instruction_pointer = instruction_pointer
        self.context = context
        self.timestamp = 0  # Will be set by the forensic logger
    
    def __str__(self) -> str:
        return (
            f"Protection bypass attempt at 0x{self.address:08x} "
            f"(IP: 0x{self.instruction_pointer:08x}): "
            f"{self.access_type} operation, "
            f"required {self.required_permission.name}, "
            f"had {self.current_permission.name}"
        )


class MemorySegment(BaseMemorySegment):
    """A specialized memory segment with security features."""
    
    def __init__(
        self,
        base_address: int,
        size: int,
        permission: MemoryPermission = MemoryPermission.READ_WRITE,
        name: str = "unnamed",
    ):
        """
        Initialize the memory segment.
        
        Args:
            base_address: Starting address of the segment
            size: Size of the segment in bytes
            permission: Access permissions for the segment
            name: Name of the segment
        """
        super().__init__(base_address, size, permission, name)
        
        # Additional security features
        self._shadow_data: Optional[bytearray] = None
        self._canaries: Dict[int, bytes] = {}
    
    def place_canary(self, offset: int, value: Optional[bytes] = None) -> bytes:
        """
        Place a canary value at the specified offset.
        
        Args:
            offset: Offset within the segment
            value: Canary value to place, or None for random
            
        Returns:
            The canary value that was placed
        """
        if offset < 0 or offset >= self.size:
            raise ValueError(f"Offset {offset} is outside segment bounds")
        
        # Generate a random canary value if none is provided
        if value is None:
            value = bytes(random.getrandbits(8) for _ in range(4))
        
        self._canaries[offset] = value
        # Write the canary to the actual memory
        for i, b in enumerate(value):
            if offset + i < self.size:
                self.data[offset + i] = b
                
        return value
    
    def check_canaries(self) -> List[Tuple[int, bytes, bytes]]:
        """
        Check all canaries and return a list of corrupted ones.
        
        Returns:
            List of (offset, expected, actual) for corrupted canaries
        """
        corrupted = []
        for offset, expected in self._canaries.items():
            actual = bytes(self.data[offset:offset + len(expected)])
            if actual != expected:
                corrupted.append((offset, expected, actual))
        return corrupted
    
    def enable_shadow_memory(self) -> None:
        """Enable shadow memory for this segment to detect unauthorized changes."""
        self._shadow_data = bytearray(self.data)
    
    def check_shadow_memory(self) -> List[int]:
        """
        Check for differences between shadow memory and actual memory.
        
        Returns:
            List of offsets where differences were found
        """
        if self._shadow_data is None:
            return []
        
        differences = []
        for i, (shadow, actual) in enumerate(zip(self._shadow_data, self.data)):
            if shadow != actual:
                differences.append(self.base_address + i)
        
        return differences
    
    def update_shadow_memory(self) -> None:
        """Update shadow memory to match current memory state."""
        if self._shadow_data is not None:
            self._shadow_data = bytearray(self.data)


class Memory(BaseMemorySystem):
    """Memory subsystem with enhanced security features."""
    
    def __init__(
        self,
        size: int = 65536,
        protection_level: MemoryProtectionLevel = MemoryProtectionLevel.STANDARD,
        enable_dep: bool = True,
        enable_aslr: bool = False,
        aslr_entropy: int = 8,  # bits of randomness for ASLR
    ):
        """
        Initialize the memory system.
        
        Args:
            size: Size of memory in bytes
            protection_level: Level of memory protection
            enable_dep: Whether to enable Data Execution Prevention
            enable_aslr: Whether to enable Address Space Layout Randomization
            aslr_entropy: Bits of randomness for ASLR
        """
        super().__init__(size, protection_level)
        self.enable_dep = enable_dep
        self.enable_aslr = enable_aslr
        self.aslr_entropy = aslr_entropy
        self.protection_events: List[ProtectionBypassAttempt] = []
        
        # ASLR offset for each memory region type
        self.aslr_offsets: Dict[str, int] = {}
        
        # Performance tracking
        self.access_count = 0
        self.protection_check_time = 0
    
    def add_segment(
        self,
        segment: MemorySegment,
        apply_aslr: bool = True
    ) -> MemorySegment:
        """
        Add a memory segment with optional ASLR applied.
        
        Args:
            segment: The memory segment to add
            apply_aslr: Whether to apply ASLR to the segment
            
        Returns:
            The added segment
        """
        # Apply ASLR if enabled and requested
        if self.enable_aslr and apply_aslr:
            # Get or create an ASLR offset for this segment type
            if segment.name not in self.aslr_offsets:
                max_offset = (1 << self.aslr_entropy) - 1
                self.aslr_offsets[segment.name] = random.randint(0, max_offset) * 16
            
            offset = self.aslr_offsets[segment.name]
            segment.base_address += offset
            segment.end_address += offset
        
        return super().add_segment(segment)
    
    def _record_protection_event(
        self,
        address: int,
        access_type: str,
        current_permission: MemoryPermission,
        required_permission: MemoryPermission,
        instruction_pointer: int,
        context: Dict[str, Any],
    ) -> None:
        """
        Record an attempt to bypass memory protection.
        
        Args:
            address: The memory address
            access_type: Type of access attempted
            current_permission: Current permission of the memory
            required_permission: Permission required for the access
            instruction_pointer: Current instruction pointer
            context: Additional context for the event
        """
        event = ProtectionBypassAttempt(
            address=address,
            access_type=access_type,
            current_permission=current_permission,
            required_permission=required_permission,
            instruction_pointer=instruction_pointer,
            context=context,
        )
        self.protection_events.append(event)
    
    def read_byte(self, address: int, context: Dict[str, Any] = None) -> int:
        """
        Read a single byte from memory, enforcing memory protections.
        
        Args:
            address: The address to read from
            context: Additional context for the read
            
        Returns:
            The byte value at the address
            
        Raises:
            SegmentationFault: If the address is not in any mapped segment
            ProtectionFault: If the read violates memory permissions
        """
        self.access_count += 1
        context = context or {}
        
        # Find the segment containing this address
        segment = self.find_segment(address)
        if segment is None:
            self._record_protection_event(
                address, "read", MemoryPermission.NONE, 
                MemoryPermission.READ, context.get("instruction_pointer", 0), context
            )
            raise SegmentationFault(
                f"Segmentation fault: address 0x{address:08x} not mapped",
                address, context
            )
        
        # Check read permission if protection is enabled
        if (self.protection_level != MemoryProtectionLevel.NONE and 
                not segment.check_permission(address, MemoryPermission.READ)):
            self._record_protection_event(
                address, "read", segment.permission, 
                MemoryPermission.READ, context.get("instruction_pointer", 0), context
            )
            if self.protection_level >= MemoryProtectionLevel.STANDARD:
                raise ProtectionFault(
                    f"Memory protection violation: cannot read from 0x{address:08x}",
                    address, "READ", segment.permission.name, context
                )
        
        # Compute the offset within the segment
        offset = segment.relative_address(address)
        
        # Create memory access record
        if self.enable_access_logging:
            access = MemoryAccess(
                address=address,
                access_type=MemoryAccessType.READ,
                context=context
            )
            self._log_access(access)
        
        return segment.data[offset]
    
    def write_byte(self, address: int, value: int, context: Dict[str, Any] = None) -> None:
        """
        Write a single byte to memory, enforcing memory protections.
        
        Args:
            address: The address to write to
            value: The byte value to write
            context: Additional context for the write
            
        Raises:
            SegmentationFault: If the address is not in any mapped segment
            ProtectionFault: If the write violates memory permissions
        """
        self.access_count += 1
        context = context or {}
        
        # Find the segment containing this address
        segment = self.find_segment(address)
        if segment is None:
            self._record_protection_event(
                address, "write", MemoryPermission.NONE, 
                MemoryPermission.WRITE, context.get("instruction_pointer", 0), context
            )
            raise SegmentationFault(
                f"Segmentation fault: address 0x{address:08x} not mapped",
                address, context
            )
        
        # Check write permission if protection is enabled
        if (self.protection_level != MemoryProtectionLevel.NONE and 
                not segment.check_permission(address, MemoryPermission.WRITE)):
            self._record_protection_event(
                address, "write", segment.permission, 
                MemoryPermission.WRITE, context.get("instruction_pointer", 0), context
            )
            if self.protection_level >= MemoryProtectionLevel.STANDARD:
                raise ProtectionFault(
                    f"Memory protection violation: cannot write to 0x{address:08x}",
                    address, "WRITE", segment.permission.name, context
                )
        
        # Compute the offset within the segment
        offset = segment.relative_address(address)
        
        # Create memory access record
        if self.enable_access_logging:
            access = MemoryAccess(
                address=address,
                access_type=MemoryAccessType.WRITE,
                value=value,
                context=context
            )
            self._log_access(access)
        
        segment.data[offset] = value & 0xFF
    
    def execute(self, address: int, context: Dict[str, Any] = None) -> int:
        """
        Execute code at the given address, enforcing DEP and other protections.
        
        Args:
            address: The address to execute from
            context: Additional context for the execution
            
        Returns:
            The instruction byte at the address
            
        Raises:
            SegmentationFault: If the address is not in any mapped segment
            ProtectionFault: If execution violates memory permissions
        """
        self.access_count += 1
        context = context or {}
        
        # Find the segment containing this address
        segment = self.find_segment(address)
        if segment is None:
            self._record_protection_event(
                address, "execute", MemoryPermission.NONE, 
                MemoryPermission.EXECUTE, context.get("instruction_pointer", 0), context
            )
            raise SegmentationFault(
                f"Segmentation fault: address 0x{address:08x} not mapped",
                address, context
            )
        
        # Check execute permission if DEP is enabled
        if (self.enable_dep and self.protection_level != MemoryProtectionLevel.NONE and 
                not segment.check_permission(address, MemoryPermission.EXECUTE)):
            self._record_protection_event(
                address, "execute", segment.permission, 
                MemoryPermission.EXECUTE, context.get("instruction_pointer", 0), context
            )
            if self.protection_level >= MemoryProtectionLevel.STANDARD:
                raise ProtectionFault(
                    f"DEP violation: cannot execute code at 0x{address:08x}",
                    address, "EXECUTE", segment.permission.name, context
                )
        
        # Compute the offset within the segment
        offset = segment.relative_address(address)
        
        # Create memory access record
        if self.enable_access_logging:
            access = MemoryAccess(
                address=address,
                access_type=MemoryAccessType.EXECUTE,
                context=context
            )
            self._log_access(access)
        
        return segment.data[offset]
    
    def read_bytes(self, address: int, count: int, context: Dict[str, Any] = None) -> bytes:
        """
        Read multiple bytes from memory, enforcing memory protections.
        
        Args:
            address: The starting address
            count: Number of bytes to read
            context: Additional context for the read
            
        Returns:
            The bytes at the specified address
        """
        result = bytearray(count)
        for i in range(count):
            result[i] = self.read_byte(address + i, context)
        return bytes(result)
    
    def write_bytes(self, address: int, data: bytes, context: Dict[str, Any] = None) -> None:
        """
        Write multiple bytes to memory, enforcing memory protections.
        
        Args:
            address: The starting address
            data: The bytes to write
            context: Additional context for the write
        """
        for i, b in enumerate(data):
            self.write_byte(address + i, b, context)
    
    def read_word(self, address: int, context: Dict[str, Any] = None) -> int:
        """
        Read a 32-bit word from memory, enforcing memory protections.
        
        Args:
            address: The address to read from
            context: Additional context for the read
            
        Returns:
            The 32-bit word at the address
        """
        data = self.read_bytes(address, 4, context)
        return struct.unpack("<I", data)[0]
    
    def write_word(self, address: int, value: int, context: Dict[str, Any] = None) -> None:
        """
        Write a 32-bit word to memory, enforcing memory protections.
        
        Args:
            address: The address to write to
            value: The word value to write
            context: Additional context for the write
        """
        data = struct.pack("<I", value)
        self.write_bytes(address, data, context)
    
    def place_stack_canaries(self, stack_segment: MemorySegment, interval: int = 64) -> List[Tuple[int, bytes]]:
        """
        Place canaries at regular intervals in the stack segment.
        
        Args:
            stack_segment: The stack segment
            interval: Interval between canaries
            
        Returns:
            List of (address, canary_value) tuples
        """
        canaries = []
        for offset in range(0, stack_segment.size, interval):
            value = stack_segment.place_canary(offset)
            canaries.append((stack_segment.base_address + offset, value))
        return canaries
    
    def check_segment_canaries(self, segment: MemorySegment) -> List[Tuple[int, bytes, bytes]]:
        """
        Check canaries in the given segment and return corrupted ones.
        
        Args:
            segment: The memory segment to check
            
        Returns:
            List of (offset, expected, actual) for corrupted canaries
        """
        return segment.check_canaries()
    
    def enable_shadow_memory(self, segment: MemorySegment) -> None:
        """
        Enable shadow memory for the given segment.
        
        Args:
            segment: The memory segment
        """
        segment.enable_shadow_memory()
    
    def check_shadow_memory(self, segment: MemorySegment) -> List[int]:
        """
        Check for unexpected changes in the segment using shadow memory.
        
        Args:
            segment: The memory segment to check
            
        Returns:
            List of addresses where unexpected changes were found
        """
        return segment.check_shadow_memory()
    
    def get_protection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about memory protection operations.
        
        Returns:
            Dictionary of memory protection statistics
        """
        return {
            "access_count": self.access_count,
            "protection_check_time": self.protection_check_time,
            "protection_events": len(self.protection_events),
            "memory_segments": len(self.segments),
        }
    
    def get_protection_events(self) -> List[ProtectionBypassAttempt]:
        """
        Get all recorded protection events.
        
        Returns:
            List of protection bypass attempts
        """
        return self.protection_events