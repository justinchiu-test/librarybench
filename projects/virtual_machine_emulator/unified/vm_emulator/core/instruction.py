"""Main virtual machine instruction representation."""

from typing import Any, Dict, List, Optional, Set, Tuple, Union

from common.core.instruction import (
    Instruction as BaseInstruction,
    InstructionType,
    InstructionSet
)

# Re-export common types and classes
InstructionType = InstructionType


class Instruction(BaseInstruction):
    """
    Extended instruction implementation for parallel computing.
    
    This extends the base instruction class with parallel-specific features.
    """
    
    def __init__(
        self,
        opcode: str,
        type: InstructionType,
        operands: List[Any],
        latency: int = 1,
        privileged: bool = False,
        metadata: Dict[str, Any] = None,
        parallel_safe: bool = True
    ):
        """
        Initialize an instruction.
        
        Args:
            opcode: The operation code (e.g., "ADD", "LOAD")
            type: The type of instruction
            operands: List of operands for the instruction
            latency: Number of cycles to execute this instruction
            privileged: Whether this is a privileged instruction
            metadata: Additional instruction-specific metadata
            parallel_safe: Whether this instruction is safe for parallel execution
        """
        super().__init__(opcode, type, operands, latency, privileged, metadata)
        self.parallel_safe = parallel_safe
    
    def is_sync(self) -> bool:
        """
        Check if this is a synchronization instruction.
        
        Returns:
            True if this is a synchronization instruction
        """
        return self.type == InstructionType.SYNC
    
    def is_atomic(self) -> bool:
        """
        Check if this is an atomic instruction.
        
        Returns:
            True if this is an atomic instruction
        """
        return self.opcode in ("CAS", "CMPXCHG", "XADD")
    
    def get_affected_addresses(self) -> List[int]:
        """
        Get the memory addresses affected by this instruction.
        
        Returns:
            List of memory addresses affected
        """
        addresses = []
        
        if self.type == InstructionType.MEMORY:
            if self.opcode == "LOAD" and len(self.operands) >= 2:
                if isinstance(self.operands[1], int):
                    addresses.append(self.operands[1])
            elif self.opcode == "STORE" and len(self.operands) >= 2:
                if isinstance(self.operands[1], int):
                    addresses.append(self.operands[1])
        
        return addresses


# Create a parallel-optimized instruction set
def create_parallel_instruction_set() -> InstructionSet:
    """
    Create an instruction set optimized for parallel computing.
    
    Returns:
        An InstructionSet instance with parallel-specific instructions
    """
    from common.core.instruction import create_common_instruction_set
    
    # Start with the common instruction set
    isa = create_common_instruction_set()
    
    # Add parallel-specific instructions
    isa.add_instruction("ATOMIC_ADD", InstructionType.SYNC, latency=3)
    isa.add_instruction("ATOMIC_SUB", InstructionType.SYNC, latency=3)
    isa.add_instruction("CMPXCHG", InstructionType.SYNC, latency=4)  # Compare and exchange
    isa.add_instruction("XADD", InstructionType.SYNC, latency=4)     # Exchange and add
    isa.add_instruction("XCHG", InstructionType.SYNC, latency=3)     # Exchange
    
    # Thread management instructions
    isa.add_instruction("FORK", InstructionType.SPECIAL, latency=6)  # Fork a new thread
    isa.add_instruction("JOIN_ALL", InstructionType.SYNC, latency=3) # Wait for all threads
    isa.add_instruction("BARRIER", InstructionType.SYNC, latency=5)  # Synchronization barrier
    
    return isa


# Default instruction set for parallel VM
DEFAULT_INSTRUCTION_SET = create_parallel_instruction_set()