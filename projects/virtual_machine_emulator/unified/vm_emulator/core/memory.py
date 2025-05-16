"""Memory system implementation for parallel computing VM."""

from typing import Dict, List, Optional, Set, Tuple, Union, Any

from common.core.memory import (
    MemorySystem as BaseMemorySystem,
    MemoryAccessType,
    MemoryPermission,
    MemoryAccess,
    MemorySegment,
    MemoryProtectionLevel
)
from common.core.exceptions import MemoryException, SegmentationFault, InvalidAddressException
from common.extensions.parallel.race_detection import RaceDetector
from common.extensions.parallel.coherence import CoherenceController, CoherenceState

# Re-export common types
MemoryAccessType = MemoryAccessType
MemoryAccess = MemoryAccess


class MemorySystem(BaseMemorySystem):
    """
    Extended memory system for parallel computing.
    
    This extends the base memory system with features specific to
    parallel computing, such as race detection.
    """
    
    def __init__(
        self,
        size: int = 2**16,
        protection_level: MemoryProtectionLevel = MemoryProtectionLevel.STANDARD,
        enable_race_detection: bool = True
    ):
        """
        Initialize the memory system.
        
        Args:
            size: Size of memory in words
            protection_level: Level of memory protection
            enable_race_detection: Whether to enable race detection
        """
        super().__init__(size, protection_level)
        
        # Use the RaceDetector from common extensions
        self.enable_race_detection = enable_race_detection
        self.race_detector = RaceDetector(enabled=enable_race_detection)
    
    def read(
        self,
        address: int,
        processor_id: Optional[int] = None,
        thread_id: Optional[str] = None,
        timestamp: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Read a value from memory with race detection.
        
        Args:
            address: Memory address to read from
            processor_id: ID of the processor performing the read
            thread_id: ID of the thread performing the read
            timestamp: Current timestamp
            context: Additional context for the operation
            
        Returns:
            Value read from memory
        """
        value = super().read(address, processor_id, thread_id, timestamp, context)
        
        # Record the access for race detection
        if self.enable_race_detection and thread_id is not None and timestamp is not None and processor_id is not None:
            self.race_detector.record_access(
                thread_id=thread_id,
                processor_id=processor_id,
                timestamp=timestamp,
                address=address,
                is_write=False,
                value=value
            )
        
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
        Write a value to memory with race detection.
        
        Args:
            address: Memory address to write to
            value: Value to write
            processor_id: ID of the processor performing the write
            thread_id: ID of the thread performing the write
            timestamp: Current timestamp
            context: Additional context for the operation
        """
        super().write(address, value, processor_id, thread_id, timestamp, context)
        
        # Record the access for race detection
        if self.enable_race_detection and thread_id is not None and timestamp is not None and processor_id is not None:
            self.race_detector.record_access(
                thread_id=thread_id,
                processor_id=processor_id,
                timestamp=timestamp,
                address=address,
                is_write=True,
                value=value
            )
    
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
        Perform atomic compare-and-swap with race detection.
        
        Args:
            address: Memory address to operate on
            expected: Expected current value
            new_value: New value to set if expected matches current
            processor_id: ID of the processor performing the operation
            thread_id: ID of the thread performing the operation
            timestamp: Current timestamp
            context: Additional context for the operation
            
        Returns:
            True if swap was performed, False otherwise
        """
        success = super().compare_and_swap(
            address, expected, new_value, 
            processor_id, thread_id, timestamp, context
        )
        
        # Record the access for race detection (as a write if successful)
        if self.enable_race_detection and thread_id is not None and timestamp is not None and processor_id is not None:
            self.race_detector.record_access(
                thread_id=thread_id,
                processor_id=processor_id,
                timestamp=timestamp,
                address=address,
                is_write=success,  # Only counts as a write if successful
                value=new_value if success else None
            )
        
        return success
    
    def get_race_conditions(self) -> List[Dict[str, Any]]:
        """
        Get detected race conditions.
        
        Returns:
            List of race condition details
        """
        return self.race_detector.get_race_conditions()
    
    def get_shared_addresses(self) -> Set[int]:
        """
        Get all shared memory addresses.
        
        Returns:
            Set of shared memory addresses
        """
        return self.race_detector.get_shared_addresses()
    
    def clear_race_conditions(self) -> None:
        """Clear detected race conditions."""
        self.race_detector.clear()


class CoherentMemorySystem(MemorySystem):
    """
    Memory system with cache coherence for parallel computing.
    
    This extends the basic memory system with cache coherence protocols
    for multi-processor systems.
    """
    
    def __init__(
        self,
        size: int = 2**16,
        protection_level: MemoryProtectionLevel = MemoryProtectionLevel.STANDARD,
        enable_race_detection: bool = True,
        num_processors: int = 4
    ):
        """
        Initialize the coherent memory system.
        
        Args:
            size: Size of memory in words
            protection_level: Level of memory protection
            enable_race_detection: Whether to enable race detection
            num_processors: Number of processors in the system
        """
        super().__init__(size, protection_level, enable_race_detection)
        
        # Initialize the coherence controller from common extensions
        self.coherence_controller = CoherenceController(
            num_processors=num_processors,
            memory_size=size
        )
        
        # Synchronize memory arrays
        self.coherence_controller.memory = self.memory
    
    def read(
        self,
        address: int,
        processor_id: Optional[int] = None,
        thread_id: Optional[str] = None,
        timestamp: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Read a value from memory through the cache hierarchy.
        
        Args:
            address: Memory address to read from
            processor_id: ID of the processor performing the read
            thread_id: ID of the thread performing the read
            timestamp: Current timestamp
            context: Additional context for the operation
            
        Returns:
            Value read from memory
        """
        # Basic bounds checking (inherited from base class)
        if not self.check_address(address):
            raise InvalidAddressException(f"Memory address out of bounds: 0x{address:08x}")
        
        # Use coherence controller if processor_id is provided
        if processor_id is not None and timestamp is not None:
            value, _ = self.coherence_controller.read(
                address=address,
                processor_id=processor_id,
                timestamp=timestamp
            )
            
            # Log the access in the base system too
            access = MemoryAccess(
                address=address,
                access_type=MemoryAccessType.READ,
                processor_id=processor_id,
                thread_id=thread_id,
                timestamp=timestamp,
                context=context
            )
            self._log_access(access)
            
            # Record the access for race detection
            if self.enable_race_detection and thread_id is not None:
                self.race_detector.record_access(
                    thread_id=thread_id,
                    processor_id=processor_id,
                    timestamp=timestamp,
                    address=address,
                    is_write=False,
                    value=value
                )
            
            return value
        else:
            # Fall back to basic memory access without coherence
            return super().read(address, processor_id, thread_id, timestamp, context)
    
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
        Write a value to memory through the cache hierarchy.
        
        Args:
            address: Memory address to write to
            value: Value to write
            processor_id: ID of the processor performing the write
            thread_id: ID of the thread performing the write
            timestamp: Current timestamp
            context: Additional context for the operation
        """
        # Basic bounds checking (inherited from base class)
        if not self.check_address(address):
            raise InvalidAddressException(f"Memory address out of bounds: 0x{address:08x}")
        
        # Use coherence controller if processor_id is provided
        if processor_id is not None and timestamp is not None:
            _ = self.coherence_controller.write(
                address=address,
                value=value,
                processor_id=processor_id,
                timestamp=timestamp
            )
            
            # Log the access in the base system too
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
            
            # Record the access for race detection
            if self.enable_race_detection and thread_id is not None:
                self.race_detector.record_access(
                    thread_id=thread_id,
                    processor_id=processor_id,
                    timestamp=timestamp,
                    address=address,
                    is_write=True,
                    value=value
                )
        else:
            # Fall back to basic memory access without coherence
            super().write(address, value, processor_id, thread_id, timestamp, context)
    
    def get_coherence_events(self) -> List[Dict[str, Any]]:
        """
        Get coherence events from the controller.
        
        Returns:
            List of coherence events
        """
        return self.coherence_controller.get_all_events()
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the cache system.
        
        Returns:
            Dictionary with cache statistics
        """
        return self.coherence_controller.get_coherence_statistics()
    
    def flush_cache(self, processor_id: int, timestamp: int) -> None:
        """
        Flush a processor's cache.
        
        Args:
            processor_id: ID of the processor
            timestamp: Current timestamp
        """
        _ = self.coherence_controller.flush_cache(processor_id, timestamp)
    
    def reset(self) -> None:
        """Reset the memory system to initial state."""
        super().reset()
        
        # Re-initialize the coherence controller
        self.coherence_controller = CoherenceController(
            num_processors=len(self.coherence_controller.caches),
            memory_size=self.size
        )
        
        # Synchronize memory arrays
        self.coherence_controller.memory = self.memory