"""
Thread management for parallel computing virtual machine.

This module provides thread management functionality for the parallel
computing virtual machine, including thread creation, scheduling, and
synchronization.
"""

import uuid
from typing import Dict, List, Optional, Set, Tuple, Any


class Thread:
    """
    Representation of a thread in the parallel computing VM.
    
    This extends the base Thread from common.core.vm with additional
    functionality specific to parallel computing.
    """
    
    def __init__(
        self,
        thread_id: str,
        entry_point: int,
        registers: Optional[Dict[str, int]] = None,
        parent_thread_id: Optional[str] = None,
        creation_time: int = 0,
        priority: int = 0,
        quantum: int = 10
    ):
        """
        Initialize a thread.
        
        Args:
            thread_id: Unique identifier for this thread
            entry_point: Starting program counter value
            registers: Initial register values
            parent_thread_id: ID of the parent thread if any
            creation_time: Time when the thread was created
            priority: Scheduling priority (higher values = higher priority)
            quantum: Time quantum for this thread (in cycles)
        """
        self.thread_id = thread_id
        self.pc = entry_point
        self.registers = registers or {}
        self.stack: List[int] = []
        self.state = "WAITING"  # Use string to avoid circular import
        self.processor_id: Optional[int] = None
        self.parent_thread_id = parent_thread_id
        self.creation_time = creation_time
        self.execution_cycles = 0
        
        # Parallel-specific attributes
        self.priority = priority
        self.quantum = quantum
        self.current_quantum = quantum
        self.last_scheduled = creation_time
        self.total_cpu_time = 0
        self.blocked_on: Optional[Dict[str, Any]] = None
        self.awaiting_threads: Set[str] = set()
        
        # For program reference
        self.program = None
    
    def __str__(self) -> str:
        """Return a string representation of the thread."""
        return (f"Thread {self.thread_id} (PC: {self.pc}, State: {self.state}, "
                f"Processor: {self.processor_id}, Priority: {self.priority})")
                

class ThreadManager:
    """
    Manages threads for the parallel VM.
    
    This class is responsible for thread creation, scheduling, and
    synchronization in a parallel computing environment.
    """
    
    def __init__(self, num_processors: int = 1, enable_priority: bool = True):
        """
        Initialize the thread manager.
        
        Args:
            num_processors: Number of processors available
            enable_priority: Whether to use priority-based scheduling
        """
        self.threads: Dict[str, Thread] = {}
        self.ready_queue: List[str] = []
        self.waiting_threads: Dict[str, Dict[str, Any]] = {}
        self.blocked_threads: Dict[str, Dict[str, Any]] = {}
        self.num_processors = num_processors
        self.enable_priority = enable_priority
        self.global_clock = 0
        
    def create_thread_id(self) -> str:
        """
        Create a unique thread ID.
        
        Returns:
            A unique thread ID
        """
        return str(uuid.uuid4())
    
    def create_thread(
        self,
        entry_point: int,
        registers: Optional[Dict[str, int]] = None,
        parent_thread_id: Optional[str] = None,
        priority: int = 0
    ) -> str:
        """
        Create a new thread.
        
        Args:
            entry_point: Starting program counter value
            registers: Initial register values
            parent_thread_id: ID of the parent thread if any
            priority: Scheduling priority (higher values = higher priority)
            
        Returns:
            ID of the created thread
        """
        thread_id = self.create_thread_id()
        thread = Thread(
            thread_id=thread_id,
            entry_point=entry_point,
            registers=registers or {},
            parent_thread_id=parent_thread_id,
            creation_time=self.global_clock,
            priority=priority
        )
        
        self.threads[thread_id] = thread
        self.ready_queue.append(thread_id)
        
        return thread_id
    
    def schedule_threads(
        self,
        processors: List[Any],
        context_switch_callback: Optional[callable] = None
    ) -> List[Tuple[int, str]]:
        """
        Schedule threads to processors.
        
        Args:
            processors: List of processor objects
            context_switch_callback: Optional callback for context switches
            
        Returns:
            List of (processor_id, thread_id) assignments
        """
        assignments = []
        
        # Sort ready queue by priority if enabled
        if self.enable_priority and self.ready_queue:
            self.ready_queue.sort(
                key=lambda tid: self.threads[tid].priority if tid in self.threads else 0,
                reverse=True  # Higher priority first
            )
        
        # Find idle processors
        idle_processors = [
            (i, p) for i, p in enumerate(processors) 
            if p.state == "IDLE" and p.current_thread_id is None
        ]
        
        # Assign threads to idle processors
        while idle_processors and self.ready_queue:
            processor_idx, processor = idle_processors.pop(0)
            thread_id = self.ready_queue.pop(0)
            
            if thread_id in self.threads:
                thread = self.threads[thread_id]
                
                # Update processor and thread state
                processor.current_thread_id = thread_id
                processor.state = "RUNNING"
                thread.state = "RUNNING"
                thread.processor_id = processor_idx
                thread.last_scheduled = self.global_clock
                thread.current_quantum = thread.quantum
                
                assignments.append((processor_idx, thread_id))
                
                # Call context switch callback if provided
                if context_switch_callback is not None:
                    context_switch_callback(processor_idx, thread_id)
        
        return assignments
    
    def update(self, global_clock: int) -> None:
        """
        Update thread manager state.
        
        Args:
            global_clock: Current global clock value
        """
        self.global_clock = global_clock
        
        # Update thread quantums
        for processor_id, thread in self._get_running_threads():
            thread.total_cpu_time += 1
            thread.current_quantum -= 1
            
            # Check for expired quantum
            if thread.current_quantum <= 0:
                thread.state = "WAITING"
                self.ready_queue.append(thread.thread_id)
    
    def _get_running_threads(self) -> List[Tuple[int, Thread]]:
        """
        Get currently running threads.
        
        Returns:
            List of (processor_id, thread) pairs
        """
        return [
            (thread.processor_id, thread)
            for thread in self.threads.values()
            if thread.state == "RUNNING" and thread.processor_id is not None
        ]
    
    def block_thread(
        self,
        thread_id: str,
        reason: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Block a thread.
        
        Args:
            thread_id: ID of the thread to block
            reason: Reason for blocking
            context: Additional context for the block
            
        Returns:
            Whether the thread was successfully blocked
        """
        if thread_id not in self.threads:
            return False
        
        thread = self.threads[thread_id]
        thread.state = "BLOCKED"
        thread.blocked_on = {"reason": reason, **context}
        
        self.blocked_threads[thread_id] = {
            "reason": reason,
            "blocked_at": self.global_clock,
            **context
        }
        
        return True
    
    def unblock_thread(self, thread_id: str) -> bool:
        """
        Unblock a thread.
        
        Args:
            thread_id: ID of the thread to unblock
            
        Returns:
            Whether the thread was successfully unblocked
        """
        if thread_id not in self.threads or thread_id not in self.blocked_threads:
            return False
        
        thread = self.threads[thread_id]
        thread.state = "WAITING"
        thread.blocked_on = None
        
        del self.blocked_threads[thread_id]
        self.ready_queue.append(thread_id)
        
        return True
    
    def join_thread(self, thread_id: str, target_thread_id: str) -> bool:
        """
        Block a thread until another thread completes.
        
        Args:
            thread_id: ID of the thread to block
            target_thread_id: ID of the thread to wait for
            
        Returns:
            Whether the join operation was successful
        """
        if thread_id not in self.threads or target_thread_id not in self.threads:
            return False
        
        target_thread = self.threads[target_thread_id]
        if target_thread.state == "TERMINATED":
            # Target already terminated, no need to block
            return True
        
        # Add thread to the target's awaiting set
        target_thread.awaiting_threads.add(thread_id)
        
        # Block the thread
        return self.block_thread(
            thread_id=thread_id,
            reason="join",
            context={"target_thread_id": target_thread_id}
        )
    
    def terminate_thread(self, thread_id: str) -> bool:
        """
        Terminate a thread and wake up any threads waiting on it.
        
        Args:
            thread_id: ID of the thread to terminate
            
        Returns:
            Whether the thread was successfully terminated
        """
        if thread_id not in self.threads:
            return False
        
        thread = self.threads[thread_id]
        thread.state = "TERMINATED"
        
        # Unblock any threads waiting on this one
        for waiting_thread_id in thread.awaiting_threads:
            self.unblock_thread(waiting_thread_id)
        
        return True
    
    def yield_thread(self, thread_id: str) -> bool:
        """
        Yield a thread's processor.
        
        Args:
            thread_id: ID of the thread to yield
            
        Returns:
            Whether the thread was successfully yielded
        """
        if thread_id not in self.threads:
            return False
        
        thread = self.threads[thread_id]
        if thread.state != "RUNNING":
            return False
        
        thread.state = "WAITING"
        self.ready_queue.append(thread_id)
        
        return True