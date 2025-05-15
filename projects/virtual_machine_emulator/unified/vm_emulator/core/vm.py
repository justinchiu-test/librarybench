"""Main virtual machine implementation for parallel computing."""

import json
import random
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from common.core.vm import (
    VirtualMachine as BaseVirtualMachine,
    VMState,
    Thread,
    ExecutionEvent
)
from common.core.memory import MemorySystem as BaseMemorySystem, MemoryPermission, MemoryAccessType
from common.core.processor import Processor as BaseProcessor, ProcessorState, PrivilegeLevel
from common.core.instruction import Instruction, InstructionType
from common.core.program import Program
from common.core.exceptions import VMException, MemoryException, ProcessorException

from vm_emulator.core.memory import MemorySystem, CoherentMemorySystem
from vm_emulator.core.processor import Processor
from vm_emulator.core.instruction import create_parallel_instruction_set


class VirtualMachine(BaseVirtualMachine):
    """
    Extended virtual machine for parallel computing research.
    
    This VM provides enhanced support for parallel algorithms,
    synchronization primitives, and race detection.
    """
    
    def __init__(
        self,
        num_processors: int = 4,
        memory_size: int = 2**16,
        random_seed: Optional[int] = None,
        enable_tracing: bool = True,
        enable_race_detection: bool = True,
        enable_cache_coherence: bool = False
    ):
        """
        Initialize the parallel computing VM.
        
        Args:
            num_processors: Number of processor cores
            memory_size: Size of memory in words
            random_seed: Seed for deterministic execution
            enable_tracing: Whether to collect execution traces
            enable_race_detection: Whether to enable race detection
            enable_cache_coherence: Whether to enable cache coherence
        """
        # Set these fields before calling parent constructor
        # because parent constructor calls _create_memory_system which needs these fields
        self.enable_race_detection = enable_race_detection
        self.enable_cache_coherence = enable_cache_coherence
        
        # Call parent constructor
        super().__init__(
            num_processors=num_processors,
            memory_size=memory_size,
            random_seed=random_seed,
            enable_tracing=enable_tracing
        )
        
        # Race condition detection
        self.shared_addresses: Set[int] = set()
        self.race_conditions: List[Dict[str, Any]] = []
        
        # Synchronization primitives
        self.locks: Dict[int, Optional[str]] = {}  # Map of lock_id -> thread_id
        self.semaphores: Dict[int, int] = {}  # Map of semaphore_id -> count
        self.barriers: Dict[int, Set[str]] = {}  # Map of barrier_id -> set of thread_ids
        
        # Stats for parallel performance analysis
        self.synchronization_events = 0
        self.barrier_stalls = 0
        self.lock_contention = 0
        
        # For testing
        self.debug_mode = False
    
    def create_thread(
        self,
        entry_point_or_program_id: Union[int, str],
        registers: Optional[Dict[str, int]] = None,
        parent_thread_id: Optional[str] = None
    ) -> str:
        """
        Create a new thread for a program or starting at an entry point.
        
        Args:
            entry_point_or_program_id: Program ID or starting program counter value
            registers: Initial register values
            parent_thread_id: ID of the parent thread if any
            
        Returns:
            ID of the created thread
        """
        # Check if entry_point_or_program_id is a program ID
        if isinstance(entry_point_or_program_id, str) and entry_point_or_program_id in self.loaded_programs:
            program = self.loaded_programs[entry_point_or_program_id]
            entry_point = program.entry_point
        else:
            # Assume it's an entry point
            program = None
            entry_point = entry_point_or_program_id
        
        # Create the thread ID and thread
        thread_id = self.create_thread_id()
        thread = Thread(
            thread_id=thread_id,
            entry_point=entry_point,
            registers=registers,
            parent_thread_id=parent_thread_id,
            creation_time=self.global_clock
        )
        
        # Add program reference for the parallel VM tests
        if program is not None:
            thread.program = program
        
        self.threads[thread_id] = thread
        self.ready_queue.append(thread_id)
        
        # Record thread creation in execution trace
        event = ExecutionEvent(
            event_type="thread_created",
            timestamp=self.global_clock,
            thread_id=thread_id,
            details={
                "parent_thread_id": parent_thread_id,
                "entry_point": entry_point,
                "program_id": entry_point_or_program_id if isinstance(entry_point_or_program_id, str) else None
            }
        )
        self.add_execution_trace(event)
        
        return thread_id
    
    def _create_memory_system(self, memory_size: int) -> BaseMemorySystem:
        """
        Create the memory system for this VM.
        
        Args:
            memory_size: Size of memory in words
            
        Returns:
            The memory system instance
        """
        if self.enable_cache_coherence:
            return CoherentMemorySystem(
                size=memory_size,
                enable_race_detection=self.enable_race_detection
            )
        else:
            return MemorySystem(
                size=memory_size,
                enable_race_detection=self.enable_race_detection
            )
    
    def _create_processors(self, num_processors: int) -> List[BaseProcessor]:
        """
        Create the processors for this VM.
        
        Args:
            num_processors: Number of processors to create
            
        Returns:
            List of processor instances
        """
        return [Processor(processor_id=i) for i in range(num_processors)]
    
    def load_program(self, program: Program) -> str:
        """
        Load a program into the VM.
        
        Args:
            program: The program to load
            
        Returns:
            The program ID
        """
        program_id = program.id
        self.loaded_programs[program_id] = program
        
        # Load the data segment into memory
        for addr, value in program.data_segment.items():
            self.memory.memory[addr] = value
        
        return program_id
    
    def get_instruction(self, address: int) -> Optional[Instruction]:
        """
        Get the instruction at the given address.
        
        Args:
            address: The memory address
            
        Returns:
            The instruction at the address, or None if not found
        """
        # Check each loaded program for the instruction
        for program in self.loaded_programs.values():
            # Handle the difference between program formats
            # vm_emulator Program uses lists while common.core.program uses dicts
            if hasattr(program, 'instructions') and isinstance(program.instructions, list):
                # vm_emulator format: instructions is a list
                if 0 <= address < len(program.instructions):
                    return program.instructions[address]
            else:
                # common.core.program format: instructions is a dict
                instruction = program.get_instruction(address)
                if instruction is not None:
                    return instruction
        
        return None
    
    def schedule_threads(self) -> None:
        """
        Schedule threads to processors using a simple round-robin approach.
        More sophisticated schedulers could be implemented in subclasses.
        """
        # Find idle processors
        idle_processors = [p for p in self.processors if not p.is_busy()]
        
        # Assign threads to idle processors
        while idle_processors and self.ready_queue:
            processor = idle_processors.pop(0)
            thread_id = self.ready_queue.pop(0)
            thread = self.threads[thread_id]
            
            # Start the thread on the processor
            processor.start_thread(
                thread_id=thread_id,
                pc=thread.pc,
                initial_registers=thread.registers
            )
            processor.state = ProcessorState.RUNNING
            thread.state = ProcessorState.RUNNING
            thread.processor_id = processor.processor_id
            
            # Record context switch
            self.context_switches += 1
            
            # Record in execution trace
            event = ExecutionEvent(
                event_type="thread_scheduled",
                timestamp=self.global_clock,
                thread_id=thread_id,
                processor_id=processor.processor_id
            )
            self.add_execution_trace(event)
            
            # Record context switch event
            event = ExecutionEvent(
                event_type="context_switch",
                timestamp=self.global_clock,
                thread_id=thread_id,
                processor_id=processor.processor_id,
                details={"reason": "schedule"}
            )
            self.add_execution_trace(event)
    
    def handle_side_effects(
        self,
        processor: BaseProcessor,
        thread: Thread,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> None:
        """
        Handle side effects from instruction execution.
        
        Args:
            processor: The processor that executed the instruction
            thread: The thread that executed the instruction
            instruction: The instruction that was executed
            side_effects: Side effects from instruction execution
        """
        # Handle memory reads
        if "memory_read" in side_effects:
            addr = side_effects["memory_read"]
            value = self.memory.read(
                address=addr,
                processor_id=processor.processor_id,
                thread_id=thread.thread_id,
                timestamp=self.global_clock
            )
            
            # Set the value in the register
            dest_reg = instruction.operands[0]
            processor.registers.set(dest_reg, value)
            
            # Record event in execution trace
            event = ExecutionEvent(
                event_type="memory_read",
                timestamp=self.global_clock,
                thread_id=thread.thread_id,
                processor_id=processor.processor_id,
                address=addr,
                details={"value": value}
            )
            self.add_execution_trace(event)
        
        # Handle memory writes
        if "memory_write" in side_effects:
            addr, value = side_effects["memory_write"]
            
            # Perform the write
            self.memory.write(
                address=addr,
                value=value,
                processor_id=processor.processor_id,
                thread_id=thread.thread_id,
                timestamp=self.global_clock
            )
            
            # Record event in execution trace
            event = ExecutionEvent(
                event_type="memory_write",
                timestamp=self.global_clock,
                thread_id=thread.thread_id,
                processor_id=processor.processor_id,
                address=addr,
                details={"value": value}
            )
            self.add_execution_trace(event)
        
        # Handle synchronization lock
        if "sync_lock" in side_effects:
            lock_id = side_effects["sync_lock"]
            
            # Initialize lock if it doesn't exist
            if lock_id not in self.locks:
                self.locks[lock_id] = None
            
            # Try to acquire the lock
            if self.locks[lock_id] is None:
                # Lock is free, acquire it
                self.locks[lock_id] = thread.thread_id
                
                # Record event in execution trace
                event = ExecutionEvent(
                    event_type="lock_acquired",
                    timestamp=self.global_clock,
                    thread_id=thread.thread_id,
                    processor_id=processor.processor_id,
                    details={"lock_id": lock_id}
                )
                self.add_execution_trace(event)
            else:
                # Lock is held, block the thread
                processor.state = ProcessorState.WAITING
                thread.state = ProcessorState.WAITING
                
                # Store reason for waiting
                self.waiting_threads[thread.thread_id] = {
                    "reason": "lock",
                    "lock_id": lock_id,
                    "blocked_at": self.global_clock,
                }
                
                # Record lock contention
                self.lock_contention += 1
                
                # Record event in execution trace
                event = ExecutionEvent(
                    event_type="lock_blocked",
                    timestamp=self.global_clock,
                    thread_id=thread.thread_id,
                    processor_id=processor.processor_id,
                    details={
                        "lock_id": lock_id,
                        "held_by": self.locks[lock_id]
                    }
                )
                self.add_execution_trace(event)
        
        # Handle synchronization unlock
        if "sync_unlock" in side_effects:
            lock_id = side_effects["sync_unlock"]
            
            # Initialize lock if it doesn't exist
            if lock_id not in self.locks:
                self.locks[lock_id] = None
            
            # Check if the lock is held by this thread
            if self.locks[lock_id] is not None and self.locks[lock_id] != thread.thread_id:
                # If another thread holds the lock, we have a problem
                event = ExecutionEvent(
                    event_type="lock_error",
                    timestamp=self.global_clock,
                    thread_id=thread.thread_id,
                    processor_id=processor.processor_id,
                    details={
                        "lock_id": lock_id,
                        "held_by": self.locks[lock_id],
                        "error": "Attempted to unlock a lock held by another thread"
                    }
                )
                self.add_execution_trace(event)
                raise VMException(
                    f"Thread {thread.thread_id} attempting to unlock lock {lock_id} "
                    f"held by thread {self.locks[lock_id]}"
                )
            
            # Release the lock
            self.locks[lock_id] = None
            
            # Record synchronization event
            self.synchronization_events += 1
            
            # Wake up the first thread waiting for this lock
            waiting_threads = [
                (waiting_id, waiting_info) 
                for waiting_id, waiting_info in self.waiting_threads.items()
                if waiting_info.get("reason") == "lock" and waiting_info.get("lock_id") == lock_id
            ]
            
            if waiting_threads:
                # Sort by blocked_at time to get the first waiting thread
                waiting_threads.sort(key=lambda x: x[1].get("blocked_at", 0))
                waiting_id, waiting_info = waiting_threads[0]
                
                # Remove from waiting and add to ready queue
                del self.waiting_threads[waiting_id]
                self.ready_queue.append(waiting_id)
                waiting_thread = self.threads[waiting_id]
                waiting_thread.state = ProcessorState.WAITING  # Will be RUNNING when scheduled
                
                # Assign lock to the unblocked thread
                self.locks[lock_id] = waiting_id
                
                # Record event in execution trace
                event = ExecutionEvent(
                    event_type="thread_unblocked",
                    timestamp=self.global_clock,
                    thread_id=waiting_id,
                    details={
                        "reason": "lock_released",
                        "lock_id": lock_id
                    }
                )
                self.add_execution_trace(event)
                
                # Record context switch event
                self.context_switches += 1
                event = ExecutionEvent(
                    event_type="context_switch",
                    timestamp=self.global_clock,
                    thread_id=waiting_id,
                    details={
                        "reason": "lock_released",
                        "lock_id": lock_id
                    }
                )
                self.add_execution_trace(event)
            
            # Record event in execution trace
            event = ExecutionEvent(
                event_type="lock_released",
                timestamp=self.global_clock,
                thread_id=thread.thread_id,
                processor_id=processor.processor_id,
                details={"lock_id": lock_id}
            )
            self.add_execution_trace(event)
        
        # Handle memory fence
        if "memory_fence" in side_effects:
            # Record event in execution trace
            event = ExecutionEvent(
                event_type="memory_fence",
                timestamp=self.global_clock,
                thread_id=thread.thread_id,
                processor_id=processor.processor_id
            )
            self.add_execution_trace(event)
        
        # Handle compare-and-swap
        if "cas_operation" in side_effects:
            addr, expected, new_value, result_reg = side_effects["cas_operation"]
            success = self.memory.compare_and_swap(
                address=addr,
                expected=expected,
                new_value=new_value,
                processor_id=processor.processor_id,
                thread_id=thread.thread_id,
                timestamp=self.global_clock
            )
            
            # Store result in the register
            processor.registers.set(result_reg, 1 if success else 0)
            
            # Record event in execution trace
            event = ExecutionEvent(
                event_type="cas_operation",
                timestamp=self.global_clock,
                thread_id=thread.thread_id,
                processor_id=processor.processor_id,
                address=addr,
                details={
                    "expected": expected,
                    "new_value": new_value,
                    "success": success
                }
            )
            self.add_execution_trace(event)
        
        # Handle thread halt
        if "halt" in side_effects:
            thread.state = ProcessorState.TERMINATED
            processor.state = ProcessorState.IDLE
            processor.current_thread_id = None
            
            # Record context switch
            self.context_switches += 1
            
            # Record event in execution trace
            event = ExecutionEvent(
                event_type="thread_halted",
                timestamp=self.global_clock,
                thread_id=thread.thread_id,
                processor_id=processor.processor_id
            )
            self.add_execution_trace(event)
            
            # Add context switch event
            event = ExecutionEvent(
                event_type="context_switch",
                timestamp=self.global_clock,
                thread_id=thread.thread_id,
                processor_id=processor.processor_id,
                details={"reason": "halt"}
            )
            self.add_execution_trace(event)
        
        # Handle thread yield
        if "yield" in side_effects:
            # Put thread back in ready queue
            self.ready_queue.append(thread.thread_id)
            
            # Clear processor
            processor.state = ProcessorState.IDLE
            processor.current_thread_id = None
            
            # Record context switch
            self.context_switches += 1
            
            # Record event in execution trace
            event = ExecutionEvent(
                event_type="thread_yielded",
                timestamp=self.global_clock,
                thread_id=thread.thread_id,
                processor_id=processor.processor_id
            )
            self.add_execution_trace(event)
            
            # Add context switch event
            event = ExecutionEvent(
                event_type="context_switch",
                timestamp=self.global_clock,
                thread_id=thread.thread_id,
                processor_id=processor.processor_id,
                details={"reason": "yield"}
            )
            self.add_execution_trace(event)
        
        # Handle thread spawn
        if "spawn_thread" in side_effects:
            func_addr, arg_addr, result_reg = side_effects["spawn_thread"]
            
            # Create a new thread starting at the function address
            new_thread_id = self.create_thread(
                entry_point=func_addr,
                parent_thread_id=thread.thread_id
            )
            
            # Store thread ID in result register
            processor.registers.set(result_reg, int(new_thread_id.split("-")[0], 16))
            
            # Pass argument address to the new thread
            new_thread = self.threads[new_thread_id]
            new_thread.registers["R0"] = arg_addr
        
        # Handle thread join
        if "join_thread" in side_effects:
            target_thread_id = side_effects["join_thread"]
            
            # Check if target thread exists
            if target_thread_id not in self.threads:
                raise VMException(f"Thread not found: {target_thread_id}")
            
            target_thread = self.threads[target_thread_id]
            
            if target_thread.state == ProcessorState.TERMINATED:
                # Target already terminated, continue execution
                pass
            else:
                # Block current thread until target completes
                processor.state = ProcessorState.WAITING
                thread.state = ProcessorState.WAITING
                
                # Store reason for waiting
                self.waiting_threads[thread.thread_id] = {
                    "reason": "join",
                    "target_thread_id": target_thread_id,
                }
                
                # Record event in execution trace
                event = ExecutionEvent(
                    event_type="thread_join_wait",
                    timestamp=self.global_clock,
                    thread_id=thread.thread_id,
                    processor_id=processor.processor_id,
                    details={"target_thread_id": target_thread_id}
                )
                self.add_execution_trace(event)
        
        # Handle barrier operations
        if "barrier" in side_effects:
            barrier_id = side_effects["barrier"]
            
            # Initialize barrier if it doesn't exist
            if barrier_id not in self.barriers:
                self.barriers[barrier_id] = set()
            
            # Add thread to barrier
            self.barriers[barrier_id].add(thread.thread_id)
            
            # Determine if all threads have reached the barrier
            # For simplicity, we'll consider running threads only
            running_threads = {t.thread_id for t in self.threads.values() 
                             if t.state != ProcessorState.TERMINATED}
            
            if self.barriers[barrier_id] == running_threads:
                # All threads reached barrier, release them
                for barrier_thread_id in self.barriers[barrier_id]:
                    # Check if thread is waiting (it might still be executing the barrier instruction)
                    if (barrier_thread_id != thread.thread_id and 
                            self.threads[barrier_thread_id].state == ProcessorState.WAITING):
                        # Remove from waiting list and add to ready queue
                        if barrier_thread_id in self.waiting_threads:
                            del self.waiting_threads[barrier_thread_id]
                        self.ready_queue.append(barrier_thread_id)
                
                # Clear the barrier
                self.barriers[barrier_id] = set()
                
                # Record event in execution trace
                event = ExecutionEvent(
                    event_type="barrier_released",
                    timestamp=self.global_clock,
                    details={"barrier_id": barrier_id, "thread_count": len(running_threads)}
                )
                self.add_execution_trace(event)
            else:
                # Not all threads have reached barrier, block this thread
                processor.state = ProcessorState.WAITING
                thread.state = ProcessorState.WAITING
                
                # Store reason for waiting
                self.waiting_threads[thread.thread_id] = {
                    "reason": "barrier",
                    "barrier_id": barrier_id,
                }
                
                # Record barrier stall
                self.barrier_stalls += 1
                
                # Record event in execution trace
                event = ExecutionEvent(
                    event_type="barrier_wait",
                    timestamp=self.global_clock,
                    thread_id=thread.thread_id,
                    processor_id=processor.processor_id,
                    details={
                        "barrier_id": barrier_id,
                        "waiting_count": len(self.barriers[barrier_id]),
                        "total_count": len(running_threads),
                    }
                )
                self.add_execution_trace(event)
    
    def get_extended_statistics(self) -> Dict[str, Any]:
        """
        Get extended parallel-specific statistics.
        
        Returns:
            Dictionary of parallel VM statistics
        """
        stats = self.get_statistics()
        
        # Add parallel-specific statistics
        stats.update({
            "synchronization_events": self.synchronization_events,
            "barrier_stalls": self.barrier_stalls,
            "lock_contention": self.lock_contention,
            "race_conditions": len(self.memory.get_race_conditions() if hasattr(self.memory, "get_race_conditions") else []),
            "shared_addresses": len(self.shared_addresses),
        })
        
        return stats
    
    def get_race_conditions(self) -> List[Dict[str, Any]]:
        """
        Get detected race conditions.
        
        Returns:
            List of race condition details
        """
        if hasattr(self.memory, "get_race_conditions"):
            return self.memory.get_race_conditions()
        return []