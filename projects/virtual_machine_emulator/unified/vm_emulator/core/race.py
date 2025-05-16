"""Race condition detection for the VM.

This module reexports functionality from the common.extensions.parallel.race_detection module
to maintain backward compatibility with the vm_emulator package.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Any

from common.extensions.parallel.race_detection import (
    AccessType,
    MemoryAccess,
    RaceCondition,
    RaceDetector as CommonRaceDetector,
)


class RaceType(Enum):
    """Types of race conditions."""
    READ_WRITE = auto()      # Read-write race condition
    WRITE_WRITE = auto()     # Write-write race condition
    ATOMICITY_VIOLATION = auto()  # Atomicity violation
    ORDER_VIOLATION = auto()  # Order violation
    DEADLOCK = auto()        # Deadlock
    LIVELOCK = auto()        # Livelock
    STARVATION = auto()      # Starvation


# Mapping between vm_emulator's RaceType and common's AccessType
_access_type_map = {
    "read": AccessType.READ,
    "write": AccessType.WRITE,
    "read_write": AccessType.READ_WRITE
}


class RaceDetector:
    """
    Race condition detector for the VM.
    
    This is a compatibility wrapper around the common.extensions.parallel.race_detection.RaceDetector
    to maintain backward compatibility with the vm_emulator package.
    """
    
    def __init__(self):
        """Initialize the race detector."""
        # Use the common race detector
        self.detector = CommonRaceDetector(enabled=True)
        
        # Backward compatibility attributes
        self.memory_accesses: Dict[int, List[Dict[str, Any]]] = {}
        self.sync_operations: Dict[str, List[Dict[str, Any]]] = {}
        self.race_conditions: List[Dict[str, Any]] = []
        self.happens_before: Dict[str, Set[str]] = {}
        self.thread_locks: Dict[str, Set[int]] = {}
        self.atomic_regions: Dict[str, List[Tuple[int, int]]] = {}
    
    def record_memory_access(
        self,
        address: int,
        access_type: str,
        thread_id: str,
        timestamp: int,
        processor_id: int,
        value: Optional[int] = None,
        lock_set: Optional[Set[int]] = None,
    ) -> None:
        """
        Record a memory access.
        
        Args:
            address: Memory address
            access_type: Type of access ("read" or "write")
            thread_id: ID of the thread
            timestamp: Global clock time
            processor_id: ID of the processor
            value: Value read or written (for writes)
            lock_set: Set of lock IDs held during access
        """
        # Convert to common format
        is_write = access_type == "write"
        
        # Record in common detector
        self.detector.record_access(
            thread_id=thread_id,
            processor_id=processor_id,
            timestamp=timestamp,
            address=address,
            is_write=is_write,
            value=value
        )
        
        # Also maintain backward compatibility data structures
        if address not in self.memory_accesses:
            self.memory_accesses[address] = []
        
        access = {
            "address": address,
            "type": access_type,
            "thread_id": thread_id,
            "timestamp": timestamp,
            "processor_id": processor_id,
            "value": value,
            "lock_set": lock_set or set(),
        }
        
        self.memory_accesses[address].append(access)
        
        # Check for race conditions after each access
        self._check_for_races(address)
    
    def record_sync_operation(
        self,
        operation: str,
        thread_id: str,
        timestamp: int,
        sync_object_id: int,
        sync_type: str,
        processor_id: int,
    ) -> None:
        """
        Record a synchronization operation.
        
        Args:
            operation: Type of operation ("acquire", "release", etc.)
            thread_id: ID of the thread
            timestamp: Global clock time
            sync_object_id: ID of the synchronization object
            sync_type: Type of synchronization object ("lock", "semaphore", etc.)
            processor_id: ID of the processor
        """
        # Initialize thread entry if needed
        if thread_id not in self.sync_operations:
            self.sync_operations[thread_id] = []
        
        # Record in backward compatibility structure
        op = {
            "operation": operation,
            "thread_id": thread_id,
            "timestamp": timestamp,
            "sync_object_id": sync_object_id,
            "sync_type": sync_type,
            "processor_id": processor_id,
        }
        
        self.sync_operations[thread_id].append(op)
        
        # Record in common detector for release/acquire operations
        if operation == "release" or operation == "acquire":
            from_thread = thread_id if operation == "release" else None
            to_thread = thread_id if operation == "acquire" else None
            
            if operation == "release" and sync_type == "lock":
                # Record that this thread released a lock, potentially establishing
                # a happens-before relationship with future acquirers
                if thread_id not in self.happens_before:
                    self.happens_before[thread_id] = set()
                
                # Remove the lock from thread's held locks
                if thread_id in self.thread_locks and sync_object_id in self.thread_locks[thread_id]:
                    self.thread_locks[thread_id].remove(sync_object_id)
            
            elif operation == "acquire" and sync_type == "lock":
                # Add to thread's held locks
                if thread_id not in self.thread_locks:
                    self.thread_locks[thread_id] = set()
                self.thread_locks[thread_id].add(sync_object_id)
                
                # Check for any release operations on this lock and establish happens-before
                for t_id, ops in self.sync_operations.items():
                    if t_id == thread_id:
                        continue
                    
                    for op in reversed(ops):  # Start from most recent
                        if (op["operation"] == "release" and 
                                op["sync_object_id"] == sync_object_id and
                                op["sync_type"] == sync_type and
                                op["timestamp"] < timestamp):
                            # Found a release of this lock before this acquisition
                            # Establish happens-before: t_id -> thread_id
                            if t_id not in self.happens_before:
                                self.happens_before[t_id] = set()
                            self.happens_before[t_id].add(thread_id)
                            
                            # Record in common detector
                            self.detector.record_synchronization(
                                from_thread=t_id,
                                to_thread=thread_id,
                                timestamp=timestamp
                            )
                            
                            break  # Stop after finding the most recent release
    
    def define_atomic_region(
        self,
        thread_id: str,
        start_address: int,
        end_address: int,
    ) -> None:
        """
        Define an expected atomic region between memory accesses.
        
        Args:
            thread_id: ID of the thread
            start_address: Starting memory address
            end_address: Ending memory address
        """
        if thread_id not in self.atomic_regions:
            self.atomic_regions[thread_id] = []
        
        self.atomic_regions[thread_id].append((start_address, end_address))
        
        # Check for existing violations in this atomic region
        self._check_atomicity_violation(thread_id, start_address, end_address)
    
    def check_deadlocks(self, waiting_graph: Dict[str, List[Tuple[str, int]]]) -> None:
        """
        Check for deadlocks in the waiting graph.
        
        Args:
            waiting_graph: Graph of thread_id -> list of (thread_id, lock_id)
        """
        # Find cycles in the waiting graph
        visited = set()
        path = []
        
        def dfs(thread_id):
            if thread_id in path:
                # Found a cycle - deadlock
                cycle_start = path.index(thread_id)
                deadlock_cycle = path[cycle_start:] + [thread_id]
                
                # Get lock information
                locks_involved = []
                for i in range(len(deadlock_cycle) - 1):
                    thread1 = deadlock_cycle[i]
                    thread2 = deadlock_cycle[i + 1]
                    
                    # Find the lock that thread1 is waiting for from thread2
                    for waiting_thread, lock_id in waiting_graph.get(thread1, []):
                        if waiting_thread == thread2:
                            locks_involved.append(lock_id)
                            break
                
                # Record the deadlock
                self.race_conditions.append({
                    "type": RaceType.DEADLOCK.name,
                    "description": f"Deadlock detected involving threads {deadlock_cycle}",
                    "threads": deadlock_cycle,
                    "locks": locks_involved,
                    "detected_at": 0,  # We don't have a timestamp here
                })
                
                return True
            
            if thread_id in visited:
                return False
            
            visited.add(thread_id)
            path.append(thread_id)
            
            for waiting_thread, _ in waiting_graph.get(thread_id, []):
                if dfs(waiting_thread):
                    return True
            
            path.pop()
            return False
        
        # Start DFS from each thread
        for thread_id in waiting_graph:
            if thread_id not in visited:
                if dfs(thread_id):
                    break
    
    def _check_atomicity_violation(self, thread_id: str, start_address: int, end_address: int) -> None:
        """
        Check for atomicity violations in a given region.
        
        Args:
            thread_id: Thread ID that owns the atomic region
            start_address: Start address of the atomic region
            end_address: End address of the atomic region
        """
        # Find all accesses in this region
        for addr in range(start_address, end_address + 1):
            if addr not in self.memory_accesses:
                continue
                
            # Find thread's accesses in this region
            thread_accesses = [a for a in self.memory_accesses[addr] if a["thread_id"] == thread_id]
            if not thread_accesses:
                continue
                
            # Find other threads' accesses in this region
            for access in self.memory_accesses[addr]:
                if access["thread_id"] == thread_id:
                    continue
                    
                # Check if this access constitutes an atomicity violation
                for thread_access in thread_accesses:
                    # Skip if no conflict
                    if access["type"] == "read" and thread_access["type"] == "read":
                        continue
                        
                    # Check if this violation already exists
                    violation_exists = False
                    for race in self.race_conditions:
                        if (race["type"] == RaceType.ATOMICITY_VIOLATION.name and
                                race["address"] == addr and
                                ((race["thread1"] == thread_id and race["thread2"] == access["thread_id"]) or
                                 (race["thread1"] == access["thread_id"] and race["thread2"] == thread_id))):
                            violation_exists = True
                            break
                            
                    if not violation_exists:
                        self.race_conditions.append({
                            "type": RaceType.ATOMICITY_VIOLATION.name,
                            "description": f"Atomicity violation at address {addr} in region {start_address}-{end_address}",
                            "address": addr,
                            "thread1": thread_id,
                            "thread2": access["thread_id"],
                            "has_happens_before": False,
                            "has_common_lock": False,
                            "detected_at": max(access["timestamp"], thread_access["timestamp"]),
                        })
    
    def _check_for_races(self, address: int) -> None:
        """
        Check for race conditions at a specific address.
        
        Args:
            address: Memory address to check
        """
        if address not in self.memory_accesses:
            return
            
        accesses = self.memory_accesses[address]
        if len(accesses) < 2:
            return
            
        # Get the latest access
        latest_access = accesses[-1]
        latest_thread = latest_access["thread_id"]
        latest_type = latest_access["type"]
        
        # Check for conflicts with previous accesses from different threads
        for prev_access in accesses[:-1]:
            prev_thread = prev_access["thread_id"]
            prev_type = prev_access["type"]
            
            # Skip if same thread
            if prev_thread == latest_thread:
                continue
                
            # Skip if both are reads
            if prev_type == "read" and latest_type == "read":
                continue
                
            # Check for atomic region violations
            is_atomicity_violation = False
            if prev_thread in self.atomic_regions:
                for start_addr, end_addr in self.atomic_regions[prev_thread]:
                    if start_addr <= address <= end_addr:
                        is_atomicity_violation = True
                        break
                        
            if latest_thread in self.atomic_regions:
                for start_addr, end_addr in self.atomic_regions[latest_thread]:
                    if start_addr <= address <= end_addr:
                        is_atomicity_violation = True
                        break
                        
            # Check if this access is protected by a common lock
            has_common_lock = False
            if "lock_set" in prev_access and "lock_set" in latest_access:
                prev_locks = prev_access["lock_set"]
                latest_locks = latest_access["lock_set"]
                common_locks = prev_locks.intersection(latest_locks)
                if common_locks:
                    has_common_lock = True
                    
            # Check for happens-before relationship
            has_happens_before = False
            if prev_thread in self.happens_before and latest_thread in self.happens_before[prev_thread]:
                has_happens_before = True
                
            # If protected by locks or happens-before, don't report a race
            if has_common_lock or has_happens_before:
                continue
                
            # Determine race type
            if is_atomicity_violation:
                race_type = RaceType.ATOMICITY_VIOLATION.name
            elif prev_type == "write" and latest_type == "write":
                race_type = RaceType.WRITE_WRITE.name
            else:
                race_type = RaceType.READ_WRITE.name
                
            # Check if this race already exists
            race_exists = False
            for race in self.race_conditions:
                if (race.get("address") == address and
                        ((race.get("thread1") == prev_thread and race.get("thread2") == latest_thread) or
                         (race.get("thread1") == latest_thread and race.get("thread2") == prev_thread))):
                    race_exists = True
                    break
                    
            if not race_exists:
                self.race_conditions.append({
                    "type": race_type,
                    "description": f"Race condition at address {address}",
                    "address": address,
                    "thread1": prev_thread,
                    "thread2": latest_thread,
                    "has_happens_before": has_happens_before,
                    "has_common_lock": has_common_lock,
                    "detected_at": max(latest_access["timestamp"], 0),
                })
    
    def check_order_violations(self) -> None:
        """Check for order violations between threads."""
        # Update race_conditions with results from common detector
        common_races = self.detector.get_race_conditions()
        
        # Convert common race conditions to vm_emulator format
        for race in common_races:
            # Skip races already recorded
            if any(r.get("address") == race["address"] and 
                   r.get("thread1") == race["thread1"] and
                   r.get("thread2") == race["thread2"] 
                   for r in self.race_conditions):
                continue
                
            race_type = RaceType.READ_WRITE.name
            if race["access_type1"] == "WRITE" and race["access_type2"] == "WRITE":
                race_type = RaceType.WRITE_WRITE.name
                
            self.race_conditions.append({
                "type": race_type,
                "description": f"Race condition at address {race['address']}",
                "address": race["address"],
                "thread1": race["thread1"],
                "thread2": race["thread2"],
                "has_happens_before": False,
                "has_common_lock": False,
                "detected_at": max(race["timestamp"], 0),
            })
        
        # Get all memory addresses that have been accessed
        for address, accesses in self.memory_accesses.items():
            # Get all threads that have accessed this address
            thread_accesses: Dict[str, List[Dict[str, Any]]] = {}
            
            for access in accesses:
                thread_id = access["thread_id"]
                if thread_id not in thread_accesses:
                    thread_accesses[thread_id] = []
                thread_accesses[thread_id].append(access)
            
            # Check for patterns indicating order violations
            for thread1 in thread_accesses:
                for thread2 in thread_accesses:
                    if thread1 == thread2:
                        continue
                    
                    # Sort accesses by timestamp
                    t1_accesses = sorted(thread_accesses[thread1], key=lambda a: a["timestamp"])
                    t2_accesses = sorted(thread_accesses[thread2], key=lambda a: a["timestamp"])
                    
                    # Skip if no accesses
                    if not t1_accesses or not t2_accesses:
                        continue
                    
                    # Look for patterns like init-read-write instead of init-write-read
                    # This is a simplified example - in practice you'd look for specific patterns
                    if (len(t1_accesses) >= 1 and len(t2_accesses) >= 2 and
                            t1_accesses[0]["type"] == "write" and  # Init
                            t2_accesses[0]["type"] == "read" and   # Read
                            t2_accesses[0]["timestamp"] < t1_accesses[0]["timestamp"]):
                        
                        # This is a potential order violation - thread2 read before thread1 initialized
                        race_found = True
                        
                        # Check if this race is already in the list
                        for race in self.race_conditions:
                            if (race["type"] == RaceType.ORDER_VIOLATION.name and
                                    race["address"] == address and
                                    race["thread1"] == thread1 and
                                    race["thread2"] == thread2):
                                race_found = False
                                break
                        
                        if race_found:
                            self.race_conditions.append({
                                "type": RaceType.ORDER_VIOLATION.name,
                                "description": (
                                    f"Order violation at address {address:#x}: "
                                    f"Thread {thread2} read uninitialized data before thread {thread1} wrote it"
                                ),
                                "address": address,
                                "thread1": thread1,
                                "thread2": thread2,
                                "accesses": t2_accesses[0:2] + [t1_accesses[0]],
                                "detected_at": t1_accesses[0]["timestamp"],
                            })
    
    def check_livelock(self, thread_stats: Dict[str, Dict[str, Any]]) -> None:
        """
        Check for livelocks.
        
        Args:
            thread_stats: Dictionary of thread statistics
        """
        # Look for threads that are active but not making progress
        suspicious_threads = []
        
        for thread_id, stats in thread_stats.items():
            # Check if the thread is active but seemingly not progressing
            if stats.get("state") != "TERMINATED" and stats.get("progress_rate", 0) < 0.1:
                suspicious_threads.append(thread_id)
        
        if len(suspicious_threads) >= 2:
            # Potential livelock
            self.race_conditions.append({
                "type": RaceType.LIVELOCK.name,
                "description": f"Potential livelock involving threads {suspicious_threads}",
                "threads": suspicious_threads,
                "detected_at": 0,  # We don't have a timestamp here
            })
    
    def check_starvation(self, thread_stats: Dict[str, Dict[str, Any]], threshold: int = 100) -> None:
        """
        Check for thread starvation.
        
        Args:
            thread_stats: Dictionary of thread statistics
            threshold: Wait time threshold for detecting starvation
        """
        # Look for threads that are waiting for a long time
        starved_threads = []
        
        for thread_id, stats in thread_stats.items():
            # Check if the thread is waiting for a long time
            if stats.get("state") == "WAITING" and stats.get("wait_time", 0) > threshold:
                starved_threads.append((thread_id, stats.get("wait_time", 0)))
        
        for thread_id, wait_time in starved_threads:
            self.race_conditions.append({
                "type": RaceType.STARVATION.name,
                "description": f"Thread {thread_id} might be starving (waiting for {wait_time} cycles)",
                "thread_id": thread_id,
                "wait_time": wait_time,
                "detected_at": 0,  # We don't have a timestamp here
            })
    
    def get_race_conditions(
        self,
        race_type: Optional[RaceType] = None,
        address: Optional[int] = None,
        thread_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get detected race conditions, optionally filtered.
        
        Args:
            race_type: Filter by race type
            address: Filter by memory address
            thread_id: Filter by thread ID
            
        Returns:
            List of race conditions
        """
        # Update race conditions from the common detector
        self.check_order_violations()
        
        result = self.race_conditions
        
        if race_type:
            result = [r for r in result if r["type"] == race_type.name]
        
        if address is not None:
            result = [r for r in result if r.get("address") == address]
        
        if thread_id:
            result = [
                r for r in result
                if r.get("thread1") == thread_id or r.get("thread2") == thread_id
                or r.get("thread_id") == thread_id
                or (r.get("threads") and thread_id in r.get("threads"))
            ]
        
        return result
    
    def get_memory_access_history(
        self,
        address: Optional[int] = None,
        thread_id: Optional[str] = None,
        access_type: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get memory access history, optionally filtered.
        
        Args:
            address: Filter by memory address
            thread_id: Filter by thread ID
            access_type: Filter by access type ("read" or "write")
            start_time: Filter by start timestamp
            end_time: Filter by end timestamp
            
        Returns:
            List of memory accesses
        """
        # Collect all accesses
        all_accesses = []
        for addr, accesses in self.memory_accesses.items():
            if address is None or addr == address:
                all_accesses.extend(accesses)
        
        # Apply filters
        result = all_accesses
        
        if thread_id:
            result = [a for a in result if a["thread_id"] == thread_id]
        
        if access_type:
            result = [a for a in result if a["type"] == access_type]
        
        if start_time is not None:
            result = [a for a in result if a["timestamp"] >= start_time]
        
        if end_time is not None:
            result = [a for a in result if a["timestamp"] <= end_time]
        
        # Sort by timestamp
        result.sort(key=lambda a: a["timestamp"])
        
        return result
    
    def get_thread_happens_before_graph(self) -> Dict[str, Set[str]]:
        """
        Get the happens-before relationship graph.
        
        Returns:
            Dictionary of thread_id -> set of thread_ids that must run after
        """
        return self.happens_before
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get race detection statistics.
        
        Returns:
            Dictionary of statistics
        """
        # Combine statistics from common detector
        common_stats = {
            "shared_addresses": len(self.detector.get_shared_addresses()),
            "race_conditions": len(self.detector.get_race_conditions()),
        }
        
        # Count race conditions by type
        race_counts = {}
        for race in self.race_conditions:
            race_type = race["type"]
            race_counts[race_type] = race_counts.get(race_type, 0) + 1
        
        # Count memory accesses
        read_count = 0
        write_count = 0
        for _, accesses in self.memory_accesses.items():
            for access in accesses:
                if access["type"] == "read":
                    read_count += 1
                elif access["type"] == "write":
                    write_count += 1
        
        return {
            "total_races": len(self.race_conditions),
            "race_counts": race_counts,
            "memory_addresses_monitored": len(self.memory_accesses),
            "total_memory_accesses": read_count + write_count,
            "read_accesses": read_count,
            "write_accesses": write_count,
            "threads_monitored": len(self.sync_operations),
            **common_stats
        }
    
    def reset(self) -> None:
        """Reset the race detector."""
        self.detector.clear()
        self.memory_accesses = {}
        self.sync_operations = {}
        self.race_conditions = []
        self.happens_before = {}
        self.thread_locks = {}
        self.atomic_regions = {}