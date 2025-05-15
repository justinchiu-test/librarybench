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
from common.core.exceptions import MemoryException, SegmentationFault


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
        
        # Race detection
        self.enable_race_detection = enable_race_detection
        self.shared_addresses: Set[int] = set()
        self.last_writer: Dict[int, Tuple[str, int]] = {}  # addr -> (thread_id, timestamp)
        self.race_conditions: List[Dict[str, Any]] = []
    
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
        
        # Check for race conditions if enabled
        if self.enable_race_detection and thread_id is not None and timestamp is not None:
            if address in self.shared_addresses:
                if address in self.last_writer:
                    last_thread, last_time = self.last_writer[address]
                    if last_thread != thread_id:
                        # Potential race condition (read after write)
                        self.race_conditions.append({
                            "type": "read_after_write",
                            "address": address,
                            "reader_thread": thread_id,
                            "reader_processor": processor_id,
                            "writer_thread": last_thread,
                            "read_time": timestamp,
                            "write_time": last_time,
                        })
        
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
        
        # Race detection if enabled
        if self.enable_race_detection and thread_id is not None and timestamp is not None:
            # Mark as shared address if accessed by multiple threads
            if address in self.last_writer and self.last_writer[address][0] != thread_id:
                self.shared_addresses.add(address)
            
            # Update last writer
            self.last_writer[address] = (thread_id, timestamp)
            
            # Check for write-write races
            if address in self.shared_addresses:
                for last_thread, last_time in self.last_writer.values():
                    if last_thread != thread_id and last_time == timestamp:
                        # Potential race condition (concurrent write)
                        self.race_conditions.append({
                            "type": "concurrent_write",
                            "address": address,
                            "writer1_thread": thread_id,
                            "writer1_processor": processor_id,
                            "writer2_thread": last_thread,
                            "time": timestamp,
                        })
    
    def get_race_conditions(self) -> List[Dict[str, Any]]:
        """
        Get detected race conditions.
        
        Returns:
            List of race condition details
        """
        return self.race_conditions
    
    def clear_race_conditions(self) -> None:
        """Clear detected race conditions."""
        self.race_conditions = []


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
        coherence_protocol: str = "MESI"
    ):
        """
        Initialize the coherent memory system.
        
        Args:
            size: Size of memory in words
            protection_level: Level of memory protection
            enable_race_detection: Whether to enable race detection
            coherence_protocol: Cache coherence protocol to use
        """
        super().__init__(size, protection_level, enable_race_detection)
        self.coherence_protocol = coherence_protocol
        self.caches: Dict[int, Any] = {}  # processor_id -> Cache
        self.bus_operations: List[Dict[str, Any]] = []
    
    def add_cache(self, processor_id: int, cache: Any) -> None:
        """
        Add a cache for a processor.
        
        Args:
            processor_id: ID of the processor
            cache: Cache instance
        """
        self.caches[processor_id] = cache
    
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
        # Check if this processor has a cache
        if processor_id is not None and processor_id in self.caches:
            cache = self.caches[processor_id]
            value, hit = cache.read(address)
            
            if hit:
                # Cache hit, just record the access
                access = MemoryAccess(
                    address=address,
                    access_type=MemoryAccessType.READ,
                    processor_id=processor_id,
                    thread_id=thread_id,
                    timestamp=timestamp,
                    context=context
                )
                self._log_access(access)
                
                # Also check for race conditions
                if self.enable_race_detection and thread_id is not None and timestamp is not None:
                    if address in self.shared_addresses:
                        if address in self.last_writer:
                            last_thread, last_time = self.last_writer[address]
                            if last_thread != thread_id:
                                # Potential race condition (read after write)
                                self.race_conditions.append({
                                    "type": "read_after_write",
                                    "address": address,
                                    "reader_thread": thread_id,
                                    "reader_processor": processor_id,
                                    "writer_thread": last_thread,
                                    "read_time": timestamp,
                                    "write_time": last_time,
                                })
                
                return value
            else:
                # Cache miss, need to go to memory
                # This will generate bus traffic in a real system
                value = super().read(address, processor_id, thread_id, timestamp, context)
                
                # Update the cache
                cache.update(address, value)
                
                return value
        else:
            # No cache, just go straight to memory
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
        # Check if this processor has a cache
        if processor_id is not None and processor_id in self.caches:
            cache = self.caches[processor_id]
            hit = cache.write(address, value)
            
            # Record the access
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
            
            # Update memory directly for simplicity
            # In a real system this would happen on cache eviction or based on coherence protocol
            super().memory[address] = value
            
            # Race detection
            if self.enable_race_detection and thread_id is not None and timestamp is not None:
                # Mark as shared address if accessed by multiple threads
                if address in self.last_writer and self.last_writer[address][0] != thread_id:
                    self.shared_addresses.add(address)
                
                # Update last writer
                self.last_writer[address] = (thread_id, timestamp)
        else:
            # No cache, just go straight to memory
            super().write(address, value, processor_id, thread_id, timestamp, context)