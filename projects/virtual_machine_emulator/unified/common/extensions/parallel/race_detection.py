"""
Race condition detection for parallel computing virtual machine.

This module provides race condition detection functionality for the
parallel computing virtual machine, including conflict detection and
race condition analysis.
"""

from enum import Enum
from typing import Dict, List, Set, Tuple, Optional, Any


class AccessType(Enum):
    """Type of memory access."""
    READ = 0
    WRITE = 1
    READ_WRITE = 2


class MemoryAccess:
    """Record of a memory access."""
    
    def __init__(
        self,
        thread_id: str,
        processor_id: int,
        timestamp: int,
        address: int,
        access_type: AccessType,
        value: Optional[int] = None
    ):
        """
        Initialize a memory access record.
        
        Args:
            thread_id: ID of the thread making the access
            processor_id: ID of the processor making the access
            timestamp: Time of the access
            address: Memory address being accessed
            access_type: Type of access (READ, WRITE, READ_WRITE)
            value: Value being written (for WRITE or READ_WRITE)
        """
        self.thread_id = thread_id
        self.processor_id = processor_id
        self.timestamp = timestamp
        self.address = address
        self.access_type = access_type
        self.value = value
    
    def __str__(self) -> str:
        """Return a string representation of the memory access."""
        return (f"MemoryAccess(thread={self.thread_id}, "
                f"processor={self.processor_id}, "
                f"time={self.timestamp}, "
                f"address={self.address}, "
                f"type={self.access_type.name}, "
                f"value={self.value})")


class RaceCondition:
    """Record of a detected race condition."""
    
    def __init__(
        self,
        address: int,
        access1: MemoryAccess,
        access2: MemoryAccess
    ):
        """
        Initialize a race condition record.
        
        Args:
            address: Memory address where the race occurred
            access1: First memory access
            access2: Second memory access
        """
        self.address = address
        self.access1 = access1
        self.access2 = access2
        self.timestamp = max(access1.timestamp, access2.timestamp)
    
    def __str__(self) -> str:
        """Return a string representation of the race condition."""
        return (f"RaceCondition(address={self.address}, "
                f"time={self.timestamp}, "
                f"thread1={self.access1.thread_id}, "
                f"thread2={self.access2.thread_id}, "
                f"type1={self.access1.access_type.name}, "
                f"type2={self.access2.access_type.name})")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the race condition to a dictionary."""
        return {
            "address": self.address,
            "timestamp": self.timestamp,
            "thread1": self.access1.thread_id,
            "thread2": self.access2.thread_id,
            "processor1": self.access1.processor_id,
            "processor2": self.access2.processor_id,
            "access_type1": self.access1.access_type.name,
            "access_type2": self.access2.access_type.name,
            "value1": self.access1.value,
            "value2": self.access2.value,
        }


class RaceDetector:
    """
    Detects race conditions in a parallel computing VM.
    
    This class monitors memory accesses and detects potential race
    conditions between threads.
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize the race detector.
        
        Args:
            enabled: Whether the race detector is enabled
        """
        self.enabled = enabled
        self.accesses: Dict[int, List[MemoryAccess]] = {}
        self.shared_addresses: Set[int] = set()
        self.race_conditions: List[RaceCondition] = []
        self.thread_accesses: Dict[str, List[MemoryAccess]] = {}
        self.happens_before: Dict[Tuple[str, str], List[int]] = {}
    
    def record_access(
        self,
        thread_id: str,
        processor_id: int,
        timestamp: int,
        address: int,
        is_write: bool,
        value: Optional[int] = None
    ) -> None:
        """
        Record a memory access.
        
        Args:
            thread_id: ID of the thread making the access
            processor_id: ID of the processor making the access
            timestamp: Time of the access
            address: Memory address being accessed
            is_write: Whether the access is a write
            value: Value being written (for writes)
        """
        if not self.enabled:
            return
        
        # Determine access type
        access_type = AccessType.WRITE if is_write else AccessType.READ
        
        # Create memory access record
        access = MemoryAccess(
            thread_id=thread_id,
            processor_id=processor_id,
            timestamp=timestamp,
            address=address,
            access_type=access_type,
            value=value
        )
        
        # Record the access
        if address not in self.accesses:
            self.accesses[address] = []
        self.accesses[address].append(access)
        
        # Track thread accesses
        if thread_id not in self.thread_accesses:
            self.thread_accesses[thread_id] = []
        self.thread_accesses[thread_id].append(access)
        
        # Check for conflicts
        self._check_conflicts(access)
    
    def _check_conflicts(self, access: MemoryAccess) -> None:
        """
        Check for conflicts with the given access.
        
        Args:
            access: The memory access to check
        """
        address = access.address
        if address not in self.accesses:
            return
        
        # Get previous accesses to this address
        prev_accesses = self.accesses[address]
        if len(prev_accesses) <= 1:
            return
        
        # Mark address as shared if accessed by multiple threads
        thread_ids = {a.thread_id for a in prev_accesses}
        if len(thread_ids) > 1:
            self.shared_addresses.add(address)
        
        # Check for conflicts with previous accesses
        for prev_access in prev_accesses[:-1]:  # Skip the current access
            if prev_access.thread_id == access.thread_id:
                # Same thread, no conflict
                continue
            
            # Check for happens-before relationship
            if self._happens_before(prev_access, access):
                # No race condition if properly synchronized
                continue
            
            # Check for conflicting access types
            if (access.access_type == AccessType.WRITE or
                    prev_access.access_type == AccessType.WRITE):
                # At least one is a write, so there's a potential race
                race = RaceCondition(address, prev_access, access)
                self.race_conditions.append(race)
    
    def _happens_before(
        self,
        access1: MemoryAccess,
        access2: MemoryAccess
    ) -> bool:
        """
        Check if access1 happens before access2.
        
        In a simplified model, we just check if they're properly ordered in time.
        A more sophisticated implementation would track synchronization events
        to establish happens-before relationships.
        
        Args:
            access1: First memory access
            access2: Second memory access
            
        Returns:
            Whether access1 happens before access2
        """
        # For now, just use timestamp ordering
        return access1.timestamp < access2.timestamp
    
    def record_synchronization(
        self,
        from_thread: str,
        to_thread: str,
        timestamp: int
    ) -> None:
        """
        Record a synchronization event between threads.
        
        This establishes a happens-before relationship between the threads.
        
        Args:
            from_thread: ID of the thread synchronizing from
            to_thread: ID of the thread synchronizing to
            timestamp: Time of the synchronization
        """
        if not self.enabled:
            return
        
        # Record the synchronization
        key = (from_thread, to_thread)
        if key not in self.happens_before:
            self.happens_before[key] = []
        self.happens_before[key].append(timestamp)
    
    def get_race_conditions(self) -> List[Dict[str, Any]]:
        """
        Get all detected race conditions.
        
        Returns:
            List of race conditions as dictionaries
        """
        return [race.to_dict() for race in self.race_conditions]
    
    def get_shared_addresses(self) -> Set[int]:
        """
        Get all shared memory addresses.
        
        Returns:
            Set of shared memory addresses
        """
        return self.shared_addresses
    
    def get_thread_access_count(self, thread_id: str) -> int:
        """
        Get the number of memory accesses by a thread.
        
        Args:
            thread_id: ID of the thread
            
        Returns:
            Number of memory accesses by the thread
        """
        if thread_id not in self.thread_accesses:
            return 0
        return len(self.thread_accesses[thread_id])
    
    def get_address_access_count(self, address: int) -> int:
        """
        Get the number of accesses to an address.
        
        Args:
            address: Memory address
            
        Returns:
            Number of accesses to the address
        """
        if address not in self.accesses:
            return 0
        return len(self.accesses[address])
    
    def clear(self) -> None:
        """Clear all recorded accesses and race conditions."""
        self.accesses.clear()
        self.shared_addresses.clear()
        self.race_conditions.clear()
        self.thread_accesses.clear()
        self.happens_before.clear()