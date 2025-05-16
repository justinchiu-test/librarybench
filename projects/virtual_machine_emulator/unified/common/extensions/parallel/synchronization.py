"""
Synchronization primitives for parallel computing virtual machine.

This module implements common synchronization primitives used in parallel
computing, such as locks, semaphores, barriers, and condition variables.
"""

from typing import Dict, List, Optional, Set, Any


class SynchronizationError(Exception):
    """Base class for synchronization-related exceptions."""
    pass


class Lock:
    """
    A mutual exclusion lock.
    
    Only one thread can hold the lock at a time. If a thread tries to acquire
    a lock that is already held, it will be blocked until the lock is released.
    """
    
    def __init__(self, lock_id: int):
        """
        Initialize a lock.
        
        Args:
            lock_id: Unique identifier for this lock
        """
        self.lock_id = lock_id
        self.holder: Optional[str] = None
        self.waiting_threads: List[str] = []
        self.acquisition_count = 0
        self.last_acquisition_time = 0
    
    def try_acquire(
        self, 
        thread_id: str,
        timestamp: int = 0
    ) -> bool:
        """
        Try to acquire the lock without blocking.
        
        Args:
            thread_id: ID of the thread trying to acquire the lock
            timestamp: Current timestamp
            
        Returns:
            Whether the lock was successfully acquired
        """
        if self.holder is None:
            # Lock is free, acquire it
            self.holder = thread_id
            self.acquisition_count += 1
            self.last_acquisition_time = timestamp
            return True
        
        # Lock is held by another thread
        return self.holder == thread_id
    
    def wait_acquire(
        self, 
        thread_id: str,
        timestamp: int = 0
    ) -> Dict[str, Any]:
        """
        Wait to acquire the lock if it's held by another thread.
        
        Args:
            thread_id: ID of the thread trying to acquire the lock
            timestamp: Current timestamp
            
        Returns:
            Dictionary with lock status and information
        """
        if self.holder is None:
            # Lock is free, acquire it
            self.holder = thread_id
            self.acquisition_count += 1
            self.last_acquisition_time = timestamp
            return {"acquired": True}
        
        if self.holder == thread_id:
            # Thread already holds the lock
            return {"acquired": True}
        
        # Lock is held by another thread, add to waiting list
        if thread_id not in self.waiting_threads:
            self.waiting_threads.append(thread_id)
        
        return {
            "acquired": False,
            "holder": self.holder,
            "wait_status": "waiting",
            "wait_position": self.waiting_threads.index(thread_id)
        }
    
    def release(
        self, 
        thread_id: str,
        timestamp: int = 0
    ) -> Dict[str, Any]:
        """
        Release the lock.
        
        Args:
            thread_id: ID of the thread trying to release the lock
            timestamp: Current timestamp
            
        Returns:
            Dictionary with release status and next thread to run
        """
        if self.holder is None:
            # Lock not held by any thread
            raise SynchronizationError("Attempted to release unheld lock")
        
        if self.holder != thread_id:
            # Lock held by another thread
            raise SynchronizationError(
                f"Thread {thread_id} attempted to release lock held by {self.holder}"
            )
        
        # Release the lock
        next_thread = None
        if self.waiting_threads:
            # Wake up the next waiting thread
            next_thread = self.waiting_threads.pop(0)
            self.holder = next_thread
            self.acquisition_count += 1
            self.last_acquisition_time = timestamp
        else:
            # No threads waiting, mark as free
            self.holder = None
        
        return {
            "released": True,
            "next_thread": next_thread
        }


class Semaphore:
    """
    A semaphore for controlling access to a shared resource.
    
    A semaphore maintains a count and blocks threads when the count
    reaches zero. It's used to limit the number of threads that can
    access a resource concurrently.
    """
    
    def __init__(self, semaphore_id: int, initial_count: int = 1):
        """
        Initialize a semaphore.
        
        Args:
            semaphore_id: Unique identifier for this semaphore
            initial_count: Initial permit count
        """
        self.semaphore_id = semaphore_id
        self.count = initial_count
        self.waiting_threads: List[str] = []
        self.acquisition_history: List[Dict[str, Any]] = []
    
    def try_acquire(
        self, 
        thread_id: str,
        timestamp: int = 0
    ) -> bool:
        """
        Try to acquire a permit from the semaphore without blocking.
        
        Args:
            thread_id: ID of the thread trying to acquire the permit
            timestamp: Current timestamp
            
        Returns:
            Whether a permit was successfully acquired
        """
        if self.count > 0:
            # Permit available, acquire it
            self.count -= 1
            self.acquisition_history.append({
                "thread_id": thread_id,
                "timestamp": timestamp,
                "operation": "acquire"
            })
            return True
        
        # No permits available
        return False
    
    def wait_acquire(
        self, 
        thread_id: str,
        timestamp: int = 0
    ) -> Dict[str, Any]:
        """
        Wait to acquire a permit if none are available.
        
        Args:
            thread_id: ID of the thread trying to acquire a permit
            timestamp: Current timestamp
            
        Returns:
            Dictionary with acquisition status and information
        """
        if self.count > 0:
            # Permit available, acquire it
            self.count -= 1
            self.acquisition_history.append({
                "thread_id": thread_id,
                "timestamp": timestamp,
                "operation": "acquire"
            })
            return {"acquired": True}
        
        # No permits available, add to waiting list
        if thread_id not in self.waiting_threads:
            self.waiting_threads.append(thread_id)
        
        return {
            "acquired": False,
            "wait_status": "waiting",
            "wait_position": self.waiting_threads.index(thread_id),
            "count": self.count
        }
    
    def release(
        self, 
        thread_id: str,
        timestamp: int = 0
    ) -> Dict[str, Any]:
        """
        Release a permit back to the semaphore.
        
        Args:
            thread_id: ID of the thread releasing the permit
            timestamp: Current timestamp
            
        Returns:
            Dictionary with release status and next thread to run
        """
        next_thread = None
        if self.waiting_threads:
            # Wake up the next waiting thread
            next_thread = self.waiting_threads.pop(0)
            # Count stays the same since we're transferring the permit
        else:
            # No threads waiting, increment count
            self.count += 1
        
        self.acquisition_history.append({
            "thread_id": thread_id,
            "timestamp": timestamp,
            "operation": "release"
        })
        
        return {
            "released": True,
            "next_thread": next_thread,
            "count": self.count
        }


class Barrier:
    """
    A synchronization barrier.
    
    A barrier blocks threads until a specified number of threads have
    reached the barrier, at which point all threads are released.
    """
    
    def __init__(self, barrier_id: int, parties: int):
        """
        Initialize a barrier.
        
        Args:
            barrier_id: Unique identifier for this barrier
            parties: Number of threads required to release the barrier
        """
        self.barrier_id = barrier_id
        self.parties = parties
        self.waiting_threads: Set[str] = set()
        self.broken = False
        self.generation = 0
    
    def await_barrier(
        self, 
        thread_id: str,
        timestamp: int = 0
    ) -> Dict[str, Any]:
        """
        Wait for the barrier to be tripped.
        
        Args:
            thread_id: ID of the thread waiting on the barrier
            timestamp: Current timestamp
            
        Returns:
            Dictionary with barrier status and information
        """
        if self.broken:
            return {"status": "broken", "generation": self.generation}
        
        # Add thread to waiting set
        self.waiting_threads.add(thread_id)
        
        if len(self.waiting_threads) >= self.parties:
            # All parties have arrived, trip the barrier
            waiting_threads = self.waiting_threads.copy()
            self.waiting_threads.clear()
            self.generation += 1
            
            return {
                "status": "tripped",
                "waiting_count": len(waiting_threads),
                "released_threads": list(waiting_threads),
                "generation": self.generation,
                "last": True  # This thread was the last to arrive
            }
        
        # Not all parties have arrived yet
        return {
            "status": "waiting",
            "waiting_count": len(self.waiting_threads),
            "needed": self.parties - len(self.waiting_threads),
            "generation": self.generation,
            "last": False
        }
    
    def reset(self) -> None:
        """Reset the barrier to its initial state."""
        self.waiting_threads.clear()
        self.broken = False
        self.generation += 1
    
    def break_barrier(self) -> Dict[str, Any]:
        """
        Break the barrier, releasing all waiting threads.
        
        Returns:
            Dictionary with barrier status and information
        """
        if not self.waiting_threads:
            return {"status": "empty", "generation": self.generation}
        
        waiting_threads = self.waiting_threads.copy()
        self.waiting_threads.clear()
        self.broken = True
        self.generation += 1
        
        return {
            "status": "broken",
            "waiting_count": len(waiting_threads),
            "released_threads": list(waiting_threads),
            "generation": self.generation
        }


class SynchronizationManager:
    """
    Manages synchronization primitives for the parallel VM.
    
    This class maintains the state of locks, semaphores, barriers, and
    provides methods for threads to interact with these primitives.
    """
    
    def __init__(self):
        """Initialize the synchronization manager."""
        self.locks: Dict[int, Lock] = {}
        self.semaphores: Dict[int, Semaphore] = {}
        self.barriers: Dict[int, Barrier] = {}
        self.synchronization_events = 0
        self.contention_events = 0
    
    def get_or_create_lock(self, lock_id: int) -> Lock:
        """
        Get or create a lock.
        
        Args:
            lock_id: ID of the lock
            
        Returns:
            The lock object
        """
        if lock_id not in self.locks:
            self.locks[lock_id] = Lock(lock_id)
        return self.locks[lock_id]
    
    def get_or_create_semaphore(
        self, 
        semaphore_id: int,
        initial_count: int = 1
    ) -> Semaphore:
        """
        Get or create a semaphore.
        
        Args:
            semaphore_id: ID of the semaphore
            initial_count: Initial permit count
            
        Returns:
            The semaphore object
        """
        if semaphore_id not in self.semaphores:
            self.semaphores[semaphore_id] = Semaphore(semaphore_id, initial_count)
        return self.semaphores[semaphore_id]
    
    def get_or_create_barrier(
        self, 
        barrier_id: int,
        parties: int
    ) -> Barrier:
        """
        Get or create a barrier.
        
        Args:
            barrier_id: ID of the barrier
            parties: Number of threads required to release the barrier
            
        Returns:
            The barrier object
        """
        if barrier_id not in self.barriers:
            self.barriers[barrier_id] = Barrier(barrier_id, parties)
        return self.barriers[barrier_id]
    
    def acquire_lock(
        self, 
        lock_id: int,
        thread_id: str,
        blocking: bool = True,
        timestamp: int = 0
    ) -> Dict[str, Any]:
        """
        Acquire a lock.
        
        Args:
            lock_id: ID of the lock
            thread_id: ID of the thread trying to acquire the lock
            blocking: Whether to block if the lock is held
            timestamp: Current timestamp
            
        Returns:
            Dictionary with acquisition status and information
        """
        lock = self.get_or_create_lock(lock_id)
        self.synchronization_events += 1
        
        if blocking:
            result = lock.wait_acquire(thread_id, timestamp)
            if not result.get("acquired", False):
                self.contention_events += 1
            return result
        else:
            result = lock.try_acquire(thread_id, timestamp)
            return {"acquired": result}
    
    def release_lock(
        self, 
        lock_id: int,
        thread_id: str,
        timestamp: int = 0
    ) -> Dict[str, Any]:
        """
        Release a lock.
        
        Args:
            lock_id: ID of the lock
            thread_id: ID of the thread releasing the lock
            timestamp: Current timestamp
            
        Returns:
            Dictionary with release status and information
        """
        if lock_id not in self.locks:
            raise SynchronizationError(f"Attempted to release non-existent lock {lock_id}")
        
        lock = self.locks[lock_id]
        self.synchronization_events += 1
        return lock.release(thread_id, timestamp)
    
    def acquire_semaphore(
        self, 
        semaphore_id: int,
        thread_id: str,
        blocking: bool = True,
        timestamp: int = 0
    ) -> Dict[str, Any]:
        """
        Acquire a permit from a semaphore.
        
        Args:
            semaphore_id: ID of the semaphore
            thread_id: ID of the thread trying to acquire a permit
            blocking: Whether to block if no permits are available
            timestamp: Current timestamp
            
        Returns:
            Dictionary with acquisition status and information
        """
        semaphore = self.get_or_create_semaphore(semaphore_id)
        self.synchronization_events += 1
        
        if blocking:
            result = semaphore.wait_acquire(thread_id, timestamp)
            if not result.get("acquired", False):
                self.contention_events += 1
            return result
        else:
            result = semaphore.try_acquire(thread_id, timestamp)
            return {"acquired": result}
    
    def release_semaphore(
        self, 
        semaphore_id: int,
        thread_id: str,
        timestamp: int = 0
    ) -> Dict[str, Any]:
        """
        Release a permit back to a semaphore.
        
        Args:
            semaphore_id: ID of the semaphore
            thread_id: ID of the thread releasing a permit
            timestamp: Current timestamp
            
        Returns:
            Dictionary with release status and information
        """
        if semaphore_id not in self.semaphores:
            raise SynchronizationError(
                f"Attempted to release non-existent semaphore {semaphore_id}"
            )
        
        semaphore = self.semaphores[semaphore_id]
        self.synchronization_events += 1
        return semaphore.release(thread_id, timestamp)
    
    def await_barrier(
        self, 
        barrier_id: int,
        thread_id: str,
        parties: int,
        timestamp: int = 0
    ) -> Dict[str, Any]:
        """
        Wait for a barrier to be tripped.
        
        Args:
            barrier_id: ID of the barrier
            thread_id: ID of the thread waiting on the barrier
            parties: Number of threads required to release the barrier
            timestamp: Current timestamp
            
        Returns:
            Dictionary with barrier status and information
        """
        barrier = self.get_or_create_barrier(barrier_id, parties)
        self.synchronization_events += 1
        return barrier.await_barrier(thread_id, timestamp)
    
    def reset_barrier(self, barrier_id: int) -> None:
        """
        Reset a barrier.
        
        Args:
            barrier_id: ID of the barrier
        """
        if barrier_id in self.barriers:
            self.barriers[barrier_id].reset()
    
    def break_barrier(self, barrier_id: int) -> Dict[str, Any]:
        """
        Break a barrier.
        
        Args:
            barrier_id: ID of the barrier
            
        Returns:
            Dictionary with barrier status and information
        """
        if barrier_id not in self.barriers:
            raise SynchronizationError(
                f"Attempted to break non-existent barrier {barrier_id}"
            )
        
        barrier = self.barriers[barrier_id]
        self.synchronization_events += 1
        return barrier.break_barrier()
    
    def get_synchronization_statistics(self) -> Dict[str, int]:
        """
        Get statistics about synchronization events.
        
        Returns:
            Dictionary with synchronization statistics
        """
        return {
            "total_events": self.synchronization_events,
            "contention_events": self.contention_events,
            "locks": len(self.locks),
            "semaphores": len(self.semaphores),
            "barriers": len(self.barriers),
        }