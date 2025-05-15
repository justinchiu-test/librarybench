"""
Instruction representation for virtual machine emulators.

This module provides a common representation of instructions that can be
used by both the security-focused and parallel computing-focused VM implementations.
"""

from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union


class InstructionType(Enum):
    """Categories of instruction types for VM emulators."""
    COMPUTE = auto()   # Arithmetic and logical operations
    MEMORY = auto()    # Memory operations (load, store)
    BRANCH = auto()    # Control flow operations (jumps, calls)
    SYNC = auto()      # Synchronization operations
    SYSTEM = auto()    # System and privileged operations
    SPECIAL = auto()   # Special or miscellaneous operations


class Instruction:
    """
    Representation of a VM instruction.
    
    This is a base class that can be extended by both implementations
    to suit their specific needs.
    """
    
    def __init__(
        self,
        opcode: str,
        type: InstructionType,
        operands: List[Any],
        latency: int = 1,
        privileged: bool = False,
        metadata: Dict[str, Any] = None
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
        """
        self.opcode = opcode
        self.type = type
        self.operands = operands
        self.latency = latency
        self.privileged = privileged
        self.metadata = metadata or {}
    
    def __str__(self) -> str:
        """Return a string representation of the instruction."""
        operands_str = ", ".join(str(op) for op in self.operands)
        return f"{self.opcode} {operands_str}"
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the instruction."""
        return (f"Instruction(opcode='{self.opcode}', type={self.type.name}, "
                f"operands={self.operands}, latency={self.latency}, "
                f"privileged={self.privileged})")
    
    def clone(self) -> 'Instruction':
        """Create a copy of this instruction."""
        return Instruction(
            opcode=self.opcode,
            type=self.type,
            operands=self.operands.copy(),
            latency=self.latency,
            privileged=self.privileged,
            metadata=self.metadata.copy()
        )
    
    def is_compute(self) -> bool:
        """Check if this is a compute instruction."""
        return self.type == InstructionType.COMPUTE
    
    def is_memory(self) -> bool:
        """Check if this is a memory instruction."""
        return self.type == InstructionType.MEMORY
    
    def is_branch(self) -> bool:
        """Check if this is a branch instruction."""
        return self.type == InstructionType.BRANCH
    
    def is_sync(self) -> bool:
        """Check if this is a synchronization instruction."""
        return self.type == InstructionType.SYNC
    
    def is_system(self) -> bool:
        """Check if this is a system instruction."""
        return self.type == InstructionType.SYSTEM
    
    def is_special(self) -> bool:
        """Check if this is a special instruction."""
        return self.type == InstructionType.SPECIAL


class InstructionSet:
    """
    A collection of instructions supported by a VM.
    
    This class represents the full instruction set architecture (ISA)
    of a virtual machine, including encoding/decoding functionality.
    """
    
    def __init__(self, name: str = "BaseISA"):
        """
        Initialize an instruction set.
        
        Args:
            name: A name for this instruction set
        """
        self.name = name
        self.instructions: Dict[str, InstructionType] = {}
        self.latencies: Dict[str, int] = {}
        self.privileged: Set[str] = set()
        
    def add_instruction(
        self,
        opcode: str,
        type: InstructionType,
        latency: int = 1,
        privileged: bool = False
    ) -> None:
        """
        Add an instruction to the instruction set.
        
        Args:
            opcode: Instruction opcode
            type: Type of instruction
            latency: Execution latency in cycles
            privileged: Whether this is a privileged instruction
        """
        self.instructions[opcode] = type
        self.latencies[opcode] = latency
        if privileged:
            self.privileged.add(opcode)
    
    def get_instruction_type(self, opcode: str) -> Optional[InstructionType]:
        """
        Get the type of an instruction by opcode.
        
        Args:
            opcode: The instruction opcode
            
        Returns:
            The instruction type, or None if not found
        """
        return self.instructions.get(opcode)
    
    def get_latency(self, opcode: str) -> int:
        """
        Get the latency of an instruction by opcode.
        
        Args:
            opcode: The instruction opcode
            
        Returns:
            The instruction latency, or 1 if not specified
        """
        return self.latencies.get(opcode, 1)
    
    def is_privileged(self, opcode: str) -> bool:
        """
        Check if an instruction is privileged.
        
        Args:
            opcode: The instruction opcode
            
        Returns:
            True if the instruction is privileged, False otherwise
        """
        return opcode in self.privileged
    
    def create_instruction(
        self, 
        opcode: str, 
        operands: List[Any],
        metadata: Dict[str, Any] = None
    ) -> Optional[Instruction]:
        """
        Create an instruction instance from opcode and operands.
        
        Args:
            opcode: The instruction opcode
            operands: List of operands
            metadata: Additional metadata
            
        Returns:
            An Instruction instance, or None if opcode is not supported
        """
        instr_type = self.get_instruction_type(opcode)
        if instr_type is None:
            return None
        
        return Instruction(
            opcode=opcode,
            type=instr_type,
            operands=operands,
            latency=self.get_latency(opcode),
            privileged=self.is_privileged(opcode),
            metadata=metadata
        )
        
    def __str__(self) -> str:
        """Return a string representation of the instruction set."""
        return f"{self.name} with {len(self.instructions)} instructions"


# Common instruction set shared between implementations
def create_common_instruction_set() -> InstructionSet:
    """
    Create a basic instruction set that can be used by both implementations.
    
    This provides a common foundation that can be extended.
    """
    isa = InstructionSet("CommonISA")
    
    # Compute instructions
    isa.add_instruction("ADD", InstructionType.COMPUTE)
    isa.add_instruction("SUB", InstructionType.COMPUTE)
    isa.add_instruction("MUL", InstructionType.COMPUTE, latency=2)
    isa.add_instruction("DIV", InstructionType.COMPUTE, latency=4)
    isa.add_instruction("AND", InstructionType.COMPUTE)
    isa.add_instruction("OR", InstructionType.COMPUTE)
    isa.add_instruction("XOR", InstructionType.COMPUTE)
    isa.add_instruction("SHL", InstructionType.COMPUTE)
    isa.add_instruction("SHR", InstructionType.COMPUTE)
    
    # Memory instructions
    isa.add_instruction("LOAD", InstructionType.MEMORY, latency=2)
    isa.add_instruction("STORE", InstructionType.MEMORY, latency=2)
    isa.add_instruction("PUSH", InstructionType.MEMORY)
    isa.add_instruction("POP", InstructionType.MEMORY)
    
    # Branch instructions
    isa.add_instruction("JMP", InstructionType.BRANCH)
    isa.add_instruction("JZ", InstructionType.BRANCH)
    isa.add_instruction("JNZ", InstructionType.BRANCH)
    isa.add_instruction("JGT", InstructionType.BRANCH)
    isa.add_instruction("JLT", InstructionType.BRANCH)
    isa.add_instruction("CALL", InstructionType.BRANCH, latency=2)
    isa.add_instruction("RET", InstructionType.BRANCH, latency=2)
    
    # Synchronization instructions
    isa.add_instruction("LOCK", InstructionType.SYNC, latency=3)
    isa.add_instruction("UNLOCK", InstructionType.SYNC, latency=2)
    isa.add_instruction("FENCE", InstructionType.SYNC, latency=3)
    isa.add_instruction("CAS", InstructionType.SYNC, latency=4)  # Compare-and-swap
    
    # System instructions
    isa.add_instruction("HALT", InstructionType.SYSTEM)
    isa.add_instruction("YIELD", InstructionType.SYSTEM)
    isa.add_instruction("SYSCALL", InstructionType.SYSTEM, latency=5, privileged=True)
    isa.add_instruction("SYSRET", InstructionType.SYSTEM, latency=3)
    
    # Special instructions
    isa.add_instruction("NOP", InstructionType.SPECIAL)
    isa.add_instruction("SPAWN", InstructionType.SPECIAL, latency=5)
    isa.add_instruction("JOIN", InstructionType.SPECIAL, latency=2)
    
    return isa