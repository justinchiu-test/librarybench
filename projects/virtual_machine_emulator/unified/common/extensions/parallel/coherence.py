"""
Memory coherence model for parallel computing virtual machine.

This module implements memory coherence protocols for the parallel computing
virtual machine, including MESI and MSI protocols.
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Any, Tuple


class CoherenceState(Enum):
    """Cache line state in a coherence protocol."""
    INVALID = 0    # Cache line is invalid
    SHARED = 1     # Cache line is shared (clean)
    EXCLUSIVE = 2  # Cache line is exclusive (clean)
    MODIFIED = 3   # Cache line is modified (dirty)
    OWNED = 4      # Cache line is owned (dirty but shared)


class CoherenceMessage(Enum):
    """Messages between caches in a coherence protocol."""
    READ = 0       # Read request
    WRITE = 1      # Write request
    INVALIDATE = 2 # Invalidate request
    WRITEBACK = 3  # Writeback notification
    UPGRADE = 4    # Upgrade to modified state
    DOWNGRADE = 5  # Downgrade to shared state
    SHARED_ACK = 6 # Acknowledgment of shared access
    EXCLUSIVE_ACK = 7 # Acknowledgment of exclusive access


class CoherenceEvent:
    """Record of a coherence event."""
    
    def __init__(
        self,
        processor_id: int,
        address: int,
        event_type: CoherenceMessage,
        old_state: CoherenceState,
        new_state: CoherenceState,
        timestamp: int,
        value: Optional[int] = None
    ):
        """
        Initialize a coherence event.
        
        Args:
            processor_id: ID of the processor involved
            address: Memory address
            event_type: Type of coherence event
            old_state: Cache line state before the event
            new_state: Cache line state after the event
            timestamp: Time of the event
            value: Memory value (for writes)
        """
        self.processor_id = processor_id
        self.address = address
        self.event_type = event_type
        self.old_state = old_state
        self.new_state = new_state
        self.timestamp = timestamp
        self.value = value
    
    def __str__(self) -> str:
        """Return a string representation of the coherence event."""
        return (f"CoherenceEvent(processor={self.processor_id}, "
                f"address={self.address}, "
                f"type={self.event_type.name}, "
                f"old_state={self.old_state.name}, "
                f"new_state={self.new_state.name}, "
                f"time={self.timestamp})")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the coherence event to a dictionary."""
        result = {
            "processor_id": self.processor_id,
            "address": self.address,
            "event_type": self.event_type.name,
            "old_state": self.old_state.name,
            "new_state": self.new_state.name,
            "timestamp": self.timestamp,
        }
        if self.value is not None:
            result["value"] = self.value
        return result


class CacheLine:
    """A cache line in a coherence protocol."""
    
    def __init__(
        self,
        address: int,
        state: CoherenceState = CoherenceState.INVALID,
        value: int = 0
    ):
        """
        Initialize a cache line.
        
        Args:
            address: Memory address
            state: Initial coherence state
            value: Initial memory value
        """
        self.address = address
        self.state = state
        self.value = value
        self.access_count = 0
        self.last_access_timestamp = 0
    
    def is_valid(self) -> bool:
        """
        Check if the cache line is valid.
        
        Returns:
            Whether the cache line is valid
        """
        return self.state != CoherenceState.INVALID
    
    def is_dirty(self) -> bool:
        """
        Check if the cache line is dirty.
        
        Returns:
            Whether the cache line is dirty
        """
        return self.state in (CoherenceState.MODIFIED, CoherenceState.OWNED)
    
    def is_shared(self) -> bool:
        """
        Check if the cache line is shared.
        
        Returns:
            Whether the cache line is shared
        """
        return self.state in (CoherenceState.SHARED, CoherenceState.OWNED)
    
    def is_exclusive(self) -> bool:
        """
        Check if the cache line is exclusive.
        
        Returns:
            Whether the cache line is exclusive
        """
        return self.state in (CoherenceState.EXCLUSIVE, CoherenceState.MODIFIED)
    
    def invalidate(self) -> None:
        """Invalidate the cache line."""
        self.state = CoherenceState.INVALID
    
    def update(
        self,
        value: int,
        state: CoherenceState,
        timestamp: int
    ) -> None:
        """
        Update the cache line.
        
        Args:
            value: New memory value
            state: New coherence state
            timestamp: Time of the update
        """
        self.value = value
        self.state = state
        self.access_count += 1
        self.last_access_timestamp = timestamp


class ProcessorCache:
    """A private cache for a processor in a coherent memory system."""
    
    def __init__(self, processor_id: int, cache_size: int = 64):
        """
        Initialize a processor cache.
        
        Args:
            processor_id: ID of the processor
            cache_size: Number of cache lines
        """
        self.processor_id = processor_id
        self.cache_size = cache_size
        self.cache_lines: Dict[int, CacheLine] = {}
        self.events: List[CoherenceEvent] = []
    
    def read(
        self,
        address: int,
        timestamp: int,
        coherence_controller: Any
    ) -> Tuple[int, List[CoherenceEvent]]:
        """
        Read from the cache.
        
        Args:
            address: Memory address to read
            timestamp: Time of the read
            coherence_controller: Coherence controller
            
        Returns:
            Tuple of (value, events)
        """
        # Check if the address is in the cache
        if address in self.cache_lines and self.cache_lines[address].is_valid():
            # Cache hit
            cache_line = self.cache_lines[address]
            old_state = cache_line.state
            
            # Update access time
            cache_line.access_count += 1
            cache_line.last_access_timestamp = timestamp
            
            # Log the read event
            event = CoherenceEvent(
                processor_id=self.processor_id,
                address=address,
                event_type=CoherenceMessage.READ,
                old_state=old_state,
                new_state=old_state,  # State doesn't change on read
                timestamp=timestamp,
                value=cache_line.value
            )
            self.events.append(event)
            
            return cache_line.value, [event]
        
        # Cache miss, need to fetch from memory
        return coherence_controller.handle_read_miss(
            processor_id=self.processor_id,
            address=address,
            timestamp=timestamp
        )
    
    def write(
        self,
        address: int,
        value: int,
        timestamp: int,
        coherence_controller: Any
    ) -> List[CoherenceEvent]:
        """
        Write to the cache.
        
        Args:
            address: Memory address to write
            value: Value to write
            timestamp: Time of the write
            coherence_controller: Coherence controller
            
        Returns:
            List of coherence events
        """
        # Check if the address is in the cache in a writable state
        if (address in self.cache_lines and 
                self.cache_lines[address].is_exclusive()):
            # Cache hit with exclusive access
            cache_line = self.cache_lines[address]
            old_state = cache_line.state
            
            # Update cache line
            cache_line.value = value
            cache_line.state = CoherenceState.MODIFIED
            cache_line.access_count += 1
            cache_line.last_access_timestamp = timestamp
            
            # Log the write event
            event = CoherenceEvent(
                processor_id=self.processor_id,
                address=address,
                event_type=CoherenceMessage.WRITE,
                old_state=old_state,
                new_state=cache_line.state,
                timestamp=timestamp,
                value=value
            )
            self.events.append(event)
            
            return [event]
        
        # Cache miss or non-exclusive state, need coherence actions
        return coherence_controller.handle_write_miss(
            processor_id=self.processor_id,
            address=address,
            value=value,
            timestamp=timestamp
        )
    
    def invalidate(
        self,
        address: int,
        timestamp: int
    ) -> Optional[CoherenceEvent]:
        """
        Invalidate a cache line.
        
        Args:
            address: Memory address to invalidate
            timestamp: Time of the invalidation
            
        Returns:
            Coherence event if the line was valid, None otherwise
        """
        if address not in self.cache_lines or not self.cache_lines[address].is_valid():
            return None
        
        cache_line = self.cache_lines[address]
        old_state = cache_line.state
        old_value = cache_line.value
        
        # Invalidate the cache line
        cache_line.invalidate()
        
        # Log the invalidation event
        event = CoherenceEvent(
            processor_id=self.processor_id,
            address=address,
            event_type=CoherenceMessage.INVALIDATE,
            old_state=old_state,
            new_state=cache_line.state,
            timestamp=timestamp,
            value=old_value
        )
        self.events.append(event)
        
        return event
    
    def update_state(
        self,
        address: int,
        state: CoherenceState,
        value: int,
        timestamp: int
    ) -> CoherenceEvent:
        """
        Update a cache line's state.
        
        Args:
            address: Memory address to update
            state: New coherence state
            value: New memory value
            timestamp: Time of the update
            
        Returns:
            Coherence event
        """
        # Ensure the cache line exists
        if address not in self.cache_lines:
            self.cache_lines[address] = CacheLine(address)
        
        cache_line = self.cache_lines[address]
        old_state = cache_line.state
        
        # Update the cache line
        cache_line.update(value, state, timestamp)
        
        # Determine event type based on state transition
        if old_state == CoherenceState.INVALID:
            if state == CoherenceState.SHARED:
                event_type = CoherenceMessage.SHARED_ACK
            elif state == CoherenceState.EXCLUSIVE or state == CoherenceState.MODIFIED:
                event_type = CoherenceMessage.EXCLUSIVE_ACK
            else:
                event_type = CoherenceMessage.READ
        elif old_state == CoherenceState.SHARED:
            if state == CoherenceState.MODIFIED:
                event_type = CoherenceMessage.UPGRADE
            elif state == CoherenceState.INVALID:
                event_type = CoherenceMessage.INVALIDATE
            else:
                event_type = CoherenceMessage.READ
        elif old_state in (CoherenceState.EXCLUSIVE, CoherenceState.MODIFIED):
            if state == CoherenceState.SHARED or state == CoherenceState.OWNED:
                event_type = CoherenceMessage.DOWNGRADE
            elif state == CoherenceState.INVALID:
                event_type = CoherenceMessage.WRITEBACK
            else:
                event_type = CoherenceMessage.WRITE
        else:
            event_type = CoherenceMessage.READ
        
        # Log the update event
        event = CoherenceEvent(
            processor_id=self.processor_id,
            address=address,
            event_type=event_type,
            old_state=old_state,
            new_state=state,
            timestamp=timestamp,
            value=value
        )
        self.events.append(event)
        
        return event
    
    def evict(self, address: int, timestamp: int) -> Optional[CoherenceEvent]:
        """
        Evict a cache line.
        
        Args:
            address: Memory address to evict
            timestamp: Time of the eviction
            
        Returns:
            Coherence event if the line was valid, None otherwise
        """
        if address not in self.cache_lines or not self.cache_lines[address].is_valid():
            return None
        
        cache_line = self.cache_lines[address]
        old_state = cache_line.state
        value = cache_line.value
        
        # Remove the cache line
        del self.cache_lines[address]
        
        # Log the eviction event
        event = CoherenceEvent(
            processor_id=self.processor_id,
            address=address,
            event_type=CoherenceMessage.WRITEBACK if cache_line.is_dirty() else CoherenceMessage.INVALIDATE,
            old_state=old_state,
            new_state=CoherenceState.INVALID,
            timestamp=timestamp,
            value=value
        )
        self.events.append(event)
        
        return event
    
    def get_events(self) -> List[Dict[str, Any]]:
        """
        Get all coherence events for this cache.
        
        Returns:
            List of coherence events as dictionaries
        """
        return [event.to_dict() for event in self.events]
    
    def clear_events(self) -> None:
        """Clear all recorded events."""
        self.events.clear()


class CoherenceController:
    """
    Controls memory coherence in a parallel computing VM.
    
    This class manages cache coherence using the MESI protocol.
    """
    
    def __init__(self, num_processors: int, memory_size: int = 2**16):
        """
        Initialize the coherence controller.
        
        Args:
            num_processors: Number of processors
            memory_size: Size of memory in words
        """
        self.num_processors = num_processors
        self.memory_size = memory_size
        self.memory = [0] * memory_size
        self.directory: Dict[int, Set[int]] = {}  # address -> set of processors
        self.caches = [ProcessorCache(i) for i in range(num_processors)]
        self.events: List[CoherenceEvent] = []
    
    def get_processor_caches(self) -> List[ProcessorCache]:
        """
        Get all processor caches.
        
        Returns:
            List of processor caches
        """
        return self.caches
    
    def read(
        self,
        address: int,
        processor_id: int,
        timestamp: int
    ) -> Tuple[int, List[CoherenceEvent]]:
        """
        Read from memory through the coherence controller.
        
        Args:
            address: Memory address to read
            processor_id: ID of the processor
            timestamp: Time of the read
            
        Returns:
            Tuple of (value, events)
        """
        # Validate inputs
        if not 0 <= processor_id < self.num_processors:
            raise ValueError(f"Invalid processor ID: {processor_id}")
        if not 0 <= address < self.memory_size:
            raise ValueError(f"Invalid memory address: {address}")
        
        # Delegate to the processor's cache
        return self.caches[processor_id].read(address, timestamp, self)
    
    def write(
        self,
        address: int,
        value: int,
        processor_id: int,
        timestamp: int
    ) -> List[CoherenceEvent]:
        """
        Write to memory through the coherence controller.
        
        Args:
            address: Memory address to write
            value: Value to write
            processor_id: ID of the processor
            timestamp: Time of the write
            
        Returns:
            List of coherence events
        """
        # Validate inputs
        if not 0 <= processor_id < self.num_processors:
            raise ValueError(f"Invalid processor ID: {processor_id}")
        if not 0 <= address < self.memory_size:
            raise ValueError(f"Invalid memory address: {address}")
        
        # Delegate to the processor's cache
        return self.caches[processor_id].write(address, value, timestamp, self)
    
    def handle_read_miss(
        self,
        processor_id: int,
        address: int,
        timestamp: int
    ) -> Tuple[int, List[CoherenceEvent]]:
        """
        Handle a read miss in the cache.
        
        Args:
            processor_id: ID of the processor
            address: Memory address
            timestamp: Time of the read
            
        Returns:
            Tuple of (value, events)
        """
        events = []
        
        # Check directory to see if any other caches have this line
        if address in self.directory and self.directory[address]:
            # Other processors have this cache line
            sharers = self.directory[address]
            
            # Find a processor with a valid copy
            for sharer_id in sharers:
                cache = self.caches[sharer_id]
                if (address in cache.cache_lines and 
                        cache.cache_lines[address].is_valid()):
                    # Get the value from the cache
                    cache_line = cache.cache_lines[address]
                    value = cache_line.value
                    
                    # If the line is in modified state, need to writeback
                    if cache_line.state == CoherenceState.MODIFIED:
                        # Writeback to memory
                        self.memory[address] = value
                        
                        # Downgrade to shared
                        event = cache.update_state(
                            address=address,
                            state=CoherenceState.SHARED,
                            value=value,
                            timestamp=timestamp
                        )
                        events.append(event)
                    
                    # Update the requesting processor's cache
                    event = self.caches[processor_id].update_state(
                        address=address,
                        state=CoherenceState.SHARED,
                        value=value,
                        timestamp=timestamp
                    )
                    events.append(event)
                    
                    # Add to directory
                    self.directory[address].add(processor_id)
                    
                    return value, events
            
            # No valid copies found, fall through to memory read
        
        # No sharers or no valid copies, read from memory
        value = self.memory[address]
        
        # Determine if this processor has exclusive access
        exclusive = (address not in self.directory or 
                    not self.directory[address] or 
                    (self.directory[address] == {processor_id}))
        
        # Update the processor's cache
        state = CoherenceState.EXCLUSIVE if exclusive else CoherenceState.SHARED
        event = self.caches[processor_id].update_state(
            address=address,
            state=state,
            value=value,
            timestamp=timestamp
        )
        events.append(event)
        
        # Update directory
        if address not in self.directory:
            self.directory[address] = set()
        self.directory[address].add(processor_id)
        
        return value, events
    
    def handle_write_miss(
        self,
        processor_id: int,
        address: int,
        value: int,
        timestamp: int
    ) -> List[CoherenceEvent]:
        """
        Handle a write miss in the cache.
        
        Args:
            processor_id: ID of the processor
            address: Memory address
            value: Value to write
            timestamp: Time of the write
            
        Returns:
            List of coherence events
        """
        events = []
        
        # Invalidate all other copies
        if address in self.directory:
            sharers = self.directory[address].copy()
            for sharer_id in sharers:
                if sharer_id != processor_id:
                    # Invalidate the sharer's copy
                    event = self.caches[sharer_id].invalidate(address, timestamp)
                    if event:
                        events.append(event)
                    
                    # Remove from directory
                    self.directory[address].remove(sharer_id)
        
        # Update the processor's cache
        event = self.caches[processor_id].update_state(
            address=address,
            state=CoherenceState.MODIFIED,
            value=value,
            timestamp=timestamp
        )
        events.append(event)
        
        # Update directory
        if address not in self.directory:
            self.directory[address] = set()
        self.directory[address].add(processor_id)
        
        return events
    
    def flush_cache(
        self,
        processor_id: int,
        timestamp: int
    ) -> List[CoherenceEvent]:
        """
        Flush a processor's cache.
        
        Args:
            processor_id: ID of the processor
            timestamp: Time of the flush
            
        Returns:
            List of coherence events
        """
        events = []
        cache = self.caches[processor_id]
        
        # Writeback all dirty lines
        addresses = list(cache.cache_lines.keys())
        for address in addresses:
            cache_line = cache.cache_lines[address]
            if cache_line.is_dirty():
                # Writeback to memory
                self.memory[address] = cache_line.value
                
                # Log the writeback
                event = CoherenceEvent(
                    processor_id=processor_id,
                    address=address,
                    event_type=CoherenceMessage.WRITEBACK,
                    old_state=cache_line.state,
                    new_state=CoherenceState.INVALID,
                    timestamp=timestamp,
                    value=cache_line.value
                )
                events.append(event)
                
                # Update directory
                if address in self.directory:
                    self.directory[address].discard(processor_id)
            
            # Invalidate the cache line
            cache.invalidate(address, timestamp)
        
        return events
    
    def get_all_events(self) -> List[Dict[str, Any]]:
        """
        Get all coherence events from all caches.
        
        Returns:
            List of coherence events as dictionaries
        """
        all_events = []
        for cache in self.caches:
            all_events.extend(cache.get_events())
        return [event.to_dict() for event in all_events]
    
    def clear_events(self) -> None:
        """Clear all recorded events."""
        for cache in self.caches:
            cache.clear_events()
        self.events.clear()
    
    def get_memory_state(self) -> Dict[int, int]:
        """
        Get the current state of memory.
        
        Returns:
            Dictionary mapping addresses to values
        """
        # Get values from memory and caches
        result = {}
        
        # Add all modified values from caches
        for processor_id, cache in enumerate(self.caches):
            for address, cache_line in cache.cache_lines.items():
                if cache_line.is_dirty():
                    result[address] = cache_line.value
        
        # Add values from memory for addresses not in result
        for address, value in enumerate(self.memory):
            if address not in result and value != 0:
                result[address] = value
        
        return result
    
    def get_coherence_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about coherence events.
        
        Returns:
            Dictionary with coherence statistics
        """
        # Count events by type
        event_counts = {}
        for cache in self.caches:
            for event in cache.events:
                event_type = event.event_type.name
                if event_type not in event_counts:
                    event_counts[event_type] = 0
                event_counts[event_type] += 1
        
        # Count cache misses
        read_misses = event_counts.get(CoherenceMessage.SHARED_ACK.name, 0) + event_counts.get(CoherenceMessage.EXCLUSIVE_ACK.name, 0)
        write_misses = event_counts.get(CoherenceMessage.UPGRADE.name, 0) + event_counts.get(CoherenceMessage.WRITEBACK.name, 0)
        
        # Count invalidations
        invalidations = event_counts.get(CoherenceMessage.INVALIDATE.name, 0)
        
        return {
            "total_events": sum(event_counts.values()),
            "read_misses": read_misses,
            "write_misses": write_misses,
            "invalidations": invalidations,
            "event_counts": event_counts,
        }