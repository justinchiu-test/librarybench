"""
Memory protection mechanisms for the virtual machine emulator.

This module provides various memory protection features, including:
- Data Execution Prevention (DEP)
- Address Space Layout Randomization (ASLR)
- Stack canaries
- Shadow memory
- Memory permissions management
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Union, Any, Callable
import random

from common.core.memory import (
    MemorySystem, MemorySegment, MemoryPermission, MemoryAccessType, MemoryException
)


class MemoryProtectionLevel(Enum):
    """Level of memory protection to apply."""
    NONE = 0       # No memory protection
    MINIMAL = 1    # Basic memory protections only
    STANDARD = 2   # Normal memory protections (DEP, basic bounds checking)
    ENHANCED = 3   # Enhanced protections (+ canaries, stricter bounds checking)
    MAXIMUM = 4    # Maximum protection (everything enabled, including shadow memory)


class MemoryProtection:
    """Configuration for memory protection mechanisms."""

    def __init__(
        self,
        level: MemoryProtectionLevel = MemoryProtectionLevel.STANDARD,
        dep_enabled: bool = True,
        aslr_enabled: bool = False,
        stack_canaries: bool = False,
        shadow_memory: bool = False,
    ):
        """
        Initialize memory protection configuration.
        
        Args:
            level: Overall protection level
            dep_enabled: Enable Data Execution Prevention
            aslr_enabled: Enable Address Space Layout Randomization
            stack_canaries: Enable stack canary protection
            shadow_memory: Enable shadow memory for leak detection
        """
        self.level = level
        
        # Set protection features based on level if not explicitly specified
        if level == MemoryProtectionLevel.NONE:
            self.dep_enabled = False
            self.aslr_enabled = False
            self.stack_canaries = False
            self.shadow_memory = False
        elif level == MemoryProtectionLevel.MINIMAL:
            self.dep_enabled = True if dep_enabled is None else dep_enabled
            self.aslr_enabled = False
            self.stack_canaries = False
            self.shadow_memory = False
        elif level == MemoryProtectionLevel.STANDARD:
            self.dep_enabled = True if dep_enabled is None else dep_enabled
            self.aslr_enabled = False if aslr_enabled is None else aslr_enabled
            self.stack_canaries = False
            self.shadow_memory = False
        elif level == MemoryProtectionLevel.ENHANCED:
            self.dep_enabled = True if dep_enabled is None else dep_enabled
            self.aslr_enabled = True if aslr_enabled is None else aslr_enabled
            self.stack_canaries = True if stack_canaries is None else stack_canaries
            self.shadow_memory = False
        elif level == MemoryProtectionLevel.MAXIMUM:
            self.dep_enabled = True if dep_enabled is None else dep_enabled
            self.aslr_enabled = True if aslr_enabled is None else aslr_enabled
            self.stack_canaries = True if stack_canaries is None else stack_canaries
            self.shadow_memory = True if shadow_memory is None else shadow_memory
        else:
            # Explicit settings
            self.dep_enabled = dep_enabled
            self.aslr_enabled = aslr_enabled
            self.stack_canaries = stack_canaries
            self.shadow_memory = shadow_memory
        
        # Internal state
        self.canary_values: Dict[int, int] = {}  # Maps address to canary value
        self.shadow_regions: Dict[int, Tuple[int, int]] = {}  # Maps original address to (shadow_address, size)
    
    def apply_to_memory(self, memory: MemorySystem) -> None:
        """
        Apply memory protection configuration to a memory system.
        
        Args:
            memory: The memory system to configure
        """
        # Set data execution prevention
        memory.enable_dep = self.dep_enabled
        
        # Apply ASLR to segment layout if enabled
        if self.aslr_enabled:
            self._apply_aslr(memory)
        
        # Set up shadow memory if enabled
        if self.shadow_memory:
            self._setup_shadow_memory(memory)
    
    def _apply_aslr(self, memory: MemorySystem) -> None:
        """
        Apply Address Space Layout Randomization to memory segments.
        
        Args:
            memory: The memory system to modify
        """
        # Save original segments to restore after randomization
        original_segments = list(memory.segments)
        memory.segments = []
        
        for segment in original_segments:
            # Apply random offset within 64KB boundary for ASLR
            # Ensure we stay page-aligned (4KB pages)
            offset = random.randint(0, 16) * 0x1000
            
            # Calculate new base address with ASLR offset
            # Keep the segment in the same general memory region
            base_region = (segment.base_address // 0x10000) * 0x10000
            new_base = base_region + offset
            
            # Create randomized segment
            new_segment = MemorySegment(
                base_address=new_base,
                size=segment.size,
                permission=segment.permission,
                name=segment.name
            )
            
            # Copy data if any exists
            if hasattr(segment, 'data') and segment.data:
                new_segment.data = bytearray(segment.data)
            
            # Add the segment to memory
            memory.add_segment(new_segment)
    
    def _setup_shadow_memory(self, memory: MemorySystem) -> None:
        """
        Set up shadow memory for leak detection and memory safety.
        
        Args:
            memory: The memory system to modify
        """
        # Create shadow memory segments for each existing segment
        shadow_segments = []
        
        for segment in memory.segments:
            # Create a shadow segment with matching size
            shadow_address = 0xA0000000 + (len(shadow_segments) * 0x1000000)
            shadow_segment = MemorySegment(
                base_address=shadow_address,
                size=segment.size,
                permission=MemoryPermission.READ_WRITE,
                name=f"shadow_{segment.name}"
            )
            
            # Initialize shadow memory with known pattern
            shadow_segment.data = bytearray([0xFD] * segment.size)
            
            # Record the mapping
            self.shadow_regions[segment.base_address] = (shadow_address, segment.size)
            
            shadow_segments.append(shadow_segment)
        
        # Add all shadow segments to memory
        for segment in shadow_segments:
            memory.add_segment(segment)
    
    def apply_to_segment(self, segment: MemorySegment, memory: MemorySystem) -> None:
        """
        Apply segment-specific protections.
        
        Args:
            segment: The segment to protect
            memory: The memory system containing the segment
        """
        # Check if the segment exists
        if segment is None or not hasattr(memory, 'segments'):
            return
            
        # Verify the segment is in memory's segment list
        segment_exists = False
        for s in memory.segments:
            if s.base_address == segment.base_address:
                segment_exists = True
                break
                
        if not segment_exists:
            return
            
        if segment.name == "stack" and self.stack_canaries:
            self._add_stack_canary(segment, memory)
    
    def _add_stack_canary(self, segment: MemorySegment, memory: MemorySystem) -> None:
        """
        Add stack canary protection to a stack segment.
        
        Args:
            segment: The stack segment
            memory: The memory system
        """
        # Calculate canary positions (every 256 bytes in the stack)
        stack_base = segment.base_address
        stack_size = segment.size
        
        # Generate random canary values
        for pos in range(stack_base, stack_base + stack_size, 256):
            # Generate a random canary value (non-zero)
            canary = random.randint(1, 0xFFFFFFFF)
            
            # Store the canary value
            memory.write_word(pos, canary, {"operation": "write_canary"})
            
            # Record the canary for later verification
            self.canary_values[pos] = canary
    
    def check_canaries(self, memory: MemorySystem) -> List[Tuple[int, int, int]]:
        """
        Check all stack canaries for corruption.
        
        Args:
            memory: The memory system
            
        Returns:
            List of corrupted canaries as tuples (address, expected, actual)
        """
        corrupted = []
        
        for address, expected in self.canary_values.items():
            try:
                actual = memory.read_word(address, {"operation": "check_canary"})
                if actual != expected:
                    corrupted.append((address, expected, actual))
            except Exception:
                # If we can't read the canary, consider it corrupted
                corrupted.append((address, expected, 0))
        
        return corrupted
    
    def get_protection_description(self) -> Dict[str, Any]:
        """
        Get a description of the current memory protection configuration.
        
        Returns:
            Dictionary describing the memory protection
        """
        return {
            "level": self.level.name,
            "features": {
                "dep_enabled": self.dep_enabled,
                "aslr_enabled": self.aslr_enabled,
                "stack_canaries": self.stack_canaries,
                "shadow_memory": self.shadow_memory,
            },
            "canary_count": len(self.canary_values),
            "shadow_regions": len(self.shadow_regions),
        }


class MemoryProtectionException(MemoryException):
    """Exception raised for memory protection violations."""
    
    def __init__(self, message: str, address: int, protection_type: str):
        super().__init__(message)
        self.address = address
        self.protection_type = protection_type
    
    def __str__(self) -> str:
        return f"{self.protection_type} violation at 0x{self.address:08x}: {super().__str__()}"


class DEPViolationException(MemoryProtectionException):
    """Exception raised when DEP is violated."""
    
    def __init__(self, address: int):
        super().__init__(
            "Attempted to execute non-executable memory",
            address,
            "DEP"
        )


class StackCanaryException(MemoryProtectionException):
    """Exception raised when a stack canary is corrupted."""
    
    def __init__(self, address: int, expected: int, actual: int):
        super().__init__(
            f"Stack canary corrupted: expected 0x{expected:08x}, got 0x{actual:08x}",
            address,
            "Stack Canary"
        )
        self.expected = expected
        self.actual = actual