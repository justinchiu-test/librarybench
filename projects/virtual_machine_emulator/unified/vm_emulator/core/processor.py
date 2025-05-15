"""Processor implementation for parallel computing VM."""

from typing import Any, Dict, List, Optional, Set, Tuple

from common.core.processor import (
    Processor as BaseProcessor,
    ProcessorState,
    PrivilegeLevel,
    RegisterSet
)
from common.core.instruction import Instruction, InstructionType
from common.core.exceptions import ProcessorException, InvalidInstructionException


# Re-export common types
ProcessorState = ProcessorState


class Processor(BaseProcessor):
    """
    Extended processor implementation for parallel computing.
    
    This extends the base processor with parallel-specific features,
    such as enhanced handling of atomic operations.
    """
    
    def __init__(
        self,
        processor_id: int,
        register_count: int = 16,
        privilege_enforcement: bool = False,  # Default to no privilege enforcement for parallel VM
        execution_log: bool = True
    ):
        """
        Initialize the processor.
        
        Args:
            processor_id: Unique ID for this processor
            register_count: Number of general purpose registers
            privilege_enforcement: Whether to enforce privilege levels
            execution_log: Whether to log detailed execution information
        """
        super().__init__(processor_id, register_count, privilege_enforcement)
        self.execution_log = execution_log
        self.last_executed_instruction: Optional[Instruction] = None
        self.instruction_trace: List[Dict[str, Any]] = []
    
    def execute_instruction(
        self,
        instruction: Instruction
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Execute a single instruction with enhancements for parallel computing.
        
        Args:
            instruction: The instruction to execute
            
        Returns:
            Tuple of (completed, side_effects):
            - completed: Whether the instruction completed in one cycle
            - side_effects: Dictionary of side effects for the VM to handle
        """
        # Store the instruction for debugging
        self.last_executed_instruction = instruction
        
        # Execute the instruction using the base implementation
        completed, side_effects = super().execute_instruction(instruction)
        
        # Log the execution if enabled
        if self.execution_log:
            self.instruction_trace.append({
                "cycle": self.cycle_count,
                "instruction": str(instruction),
                "completed": completed,
                "pc": self.registers.get_pc(),
                "side_effects": side_effects.copy() if side_effects else None
            })
        
        return completed, side_effects
    
    def _execute_sync(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> None:
        """
        Execute a synchronization instruction with enhanced parallel support.
        
        This extends the base implementation with support for more
        parallel synchronization primitives.
        
        Args:
            instruction: The synchronization instruction to execute
            side_effects: Dictionary to store side effects
        """
        # Handle common sync operations first
        if instruction.opcode in ("LOCK", "UNLOCK", "FENCE", "CAS"):
            # Use the base implementation
            super()._execute_sync(instruction, side_effects)
        
        # Handle extended parallel operations
        elif instruction.opcode == "ATOMIC_ADD":
            if len(instruction.operands) >= 3:
                dest_reg = instruction.operands[0]
                addr = self._get_operand_value(instruction.operands[1])
                value = self._get_operand_value(instruction.operands[2])
                
                # Create side effect for atomic add
                side_effects["atomic_add"] = (addr, value, dest_reg)
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        elif instruction.opcode == "ATOMIC_SUB":
            if len(instruction.operands) >= 3:
                dest_reg = instruction.operands[0]
                addr = self._get_operand_value(instruction.operands[1])
                value = self._get_operand_value(instruction.operands[2])
                
                # Create side effect for atomic sub
                side_effects["atomic_sub"] = (addr, value, dest_reg)
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        elif instruction.opcode == "BARRIER":
            if len(instruction.operands) >= 1:
                barrier_id = self._get_operand_value(instruction.operands[0])
                side_effects["barrier"] = barrier_id
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        elif instruction.opcode == "JOIN_ALL":
            side_effects["join_all"] = True
        
        else:
            # Unknown sync instruction, defer to base class
            super()._execute_sync(instruction, side_effects)
    
    def _execute_special(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> bool:
        """
        Execute a special instruction with enhanced parallel support.
        
        Args:
            instruction: The special instruction to execute
            side_effects: Dictionary to store side effects
            
        Returns:
            Whether to increment the PC after execution
        """
        if instruction.opcode == "FORK":
            if len(instruction.operands) >= 2:
                func_addr = self._get_operand_value(instruction.operands[0])
                arg_reg = instruction.operands[1]
                arg_value = self.registers.get(arg_reg)
                
                # Create side effect for fork
                side_effects["fork"] = (func_addr, arg_value)
                
                return True
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        else:
            # Unknown special instruction, defer to base class
            return super()._execute_special(instruction, side_effects)
    
    def get_execution_trace(self) -> List[Dict[str, Any]]:
        """
        Get the instruction execution trace.
        
        Returns:
            List of executed instructions with details
        """
        return self.instruction_trace
    
    def reset_trace(self) -> None:
        """Clear the execution trace."""
        self.instruction_trace = []