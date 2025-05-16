"""Processor implementation for parallel computing VM."""

from typing import Any, Dict, List, Optional, Set, Tuple
import sys

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
        
        # Initialize registers with numeric names (R0, R1, etc.)
        # This is needed for tests
        numeric_registers = {}
        for i in range(register_count):
            numeric_registers[f"R{i}"] = 0
        self.registers.registers.update(numeric_registers)
    
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
        
        # For LOAD instructions with immediate values, handle specially for parallel VM
        if instruction.opcode == "LOAD" and len(instruction.operands) >= 2:
            dest_reg = instruction.operands[0]
            src_operand = instruction.operands[1]
            
            # If it's an immediate value, set the register directly
            if isinstance(src_operand, int):
                self.registers.set(dest_reg, src_operand)
                # Save original PC before incrementing it
                old_pc = self.registers.get_pc()
                # Increment PC to move to next instruction
                self.registers.set_pc(old_pc + 1)
                return True, {"registers_modified": [dest_reg], "pc_increment": True}
        
        # Execute the instruction using the base implementation
        completed, side_effects = super().execute_instruction(instruction)
        
        # Log the execution if enabled
        if self.execution_log:
            trace_entry = {
                "cycle": self.cycle_count,
                "instruction": str(instruction),
                "completed": completed,
                "pc": self.registers.get_pc()
            }
            
            if side_effects is not None:
                trace_entry["side_effects"] = side_effects.copy()
            
            self.instruction_trace.append(trace_entry)
        
        # Ensure side_effects exists
        if side_effects is None:
            side_effects = {}
            
        return completed, side_effects
    
    def _execute_compute(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> None:
        """
        Execute a compute instruction with parallel VM enhancements.
        
        Args:
            instruction: The compute instruction to execute
            side_effects: Dictionary to store side effects
        """
        # Handle ADD operation directly in the parallel processor
        if instruction.opcode == "ADD" and len(instruction.operands) >= 3:
            dest_reg = instruction.operands[0]
            src1 = instruction.operands[1]
            src2 = instruction.operands[2]
            
            # Get src values, either from registers or immediate values
            src1_val = self.registers.get(src1) if isinstance(src1, str) and src1 in self.registers.registers else int(src1)
            src2_val = self.registers.get(src2) if isinstance(src2, str) and src2 in self.registers.registers else int(src2)
            
            # Compute result
            result = src1_val + src2_val
            
            # Set result register
            self.registers.set(dest_reg, result)
            
            # Record modified registers in side effects
            side_effects["registers_modified"] = [dest_reg]
            
            # Save original PC before incrementing it
            old_pc = self.registers.get_pc()
            # Increment PC to move to next instruction
            self.registers.set_pc(old_pc + 1)
            side_effects["pc_increment"] = True
            
            # Return immediately without calling super
            return
            
        # For other compute operations, use the base implementation
        super()._execute_compute(instruction, side_effects)
        
    def _execute_memory(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> None:
        """
        Execute a memory instruction with parallel VM enhancements.
        
        Args:
            instruction: The memory instruction to execute
            side_effects: Dictionary to store side effects
        """
        # Handle STORE instruction specially for parallel VM
        if instruction.opcode == "STORE" and len(instruction.operands) >= 2:
            src_reg = instruction.operands[0]
            addr_operand = instruction.operands[1]
            
            # Get the value to store
            value = self.registers.get(src_reg)
            
            # Get the address
            addr = self._get_operand_value(addr_operand)
            
            # Set up the memory write side effect
            side_effects["memory_write"] = (addr, value)
            
            # Save original PC before incrementing it
            old_pc = self.registers.get_pc()
            # Increment PC to move to next instruction
            self.registers.set_pc(old_pc + 1)
            side_effects["pc_increment"] = True
            
            # Return immediately without calling super
            return
            
        # For other memory operations, use the base implementation
        super()._execute_memory(instruction, side_effects)
    
    def _execute_branch(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> bool:
        """
        Execute a branch instruction with enhanced handling for the parallel VM.
        
        Args:
            instruction: The branch instruction to execute
            side_effects: Dictionary to store side effects
            
        Returns:
            Whether to increment the PC after execution
        """
        # Handle JMP instruction
        if instruction.opcode == "JMP":
            if len(instruction.operands) >= 1:
                target = self._get_operand_value(instruction.operands[0])
                
                # Set the PC directly to the target
                self.registers.set_pc(target)
                side_effects["pc_set"] = target
                
                # Record the jump for debugging
                side_effects["branch_taken"] = True
                side_effects["branch_target"] = target
                side_effects["branch_type"] = "unconditional"
                
                # Record control flow event
                self._record_control_flow(
                    self.registers.get_pc(),
                    target,
                    "jump",
                    instruction.opcode,
                    True
                )
                
                # Don't increment PC since we set it directly
                return False
        
        # Handle JZ (Jump if Zero)
        elif instruction.opcode == "JZ" or instruction.opcode == "JEQ":
            if len(instruction.operands) >= 2:
                condition_reg = instruction.operands[0]
                target = self._get_operand_value(instruction.operands[1])
                
                # Get the condition value
                condition_value = self.registers.get(condition_reg)
                
                if condition_value == 0:
                    # Condition is true, take the jump
                    self.registers.set_pc(target)
                    side_effects["pc_set"] = target
                    side_effects["branch_taken"] = True
                    side_effects["branch_target"] = target
                    side_effects["branch_type"] = "conditional"
                    
                    # Record control flow event
                    self._record_control_flow(
                        self.registers.get_pc(),
                        target,
                        "conditional_jump",
                        instruction.opcode,
                        True
                    )
                    
                    return False
                else:
                    # Condition is false, don't take the jump
                    side_effects["branch_taken"] = False
                    side_effects["branch_type"] = "conditional"
                    return True  # Increment PC normally
        
        # Handle JNZ (Jump if Not Zero)
        elif instruction.opcode == "JNZ" or instruction.opcode == "JNE":
            if len(instruction.operands) >= 2:
                condition_reg = instruction.operands[0]
                target = self._get_operand_value(instruction.operands[1])
                
                # Get the condition value
                condition_value = self.registers.get(condition_reg)
                
                if condition_value != 0:
                    # Condition is true, take the jump
                    self.registers.set_pc(target)
                    side_effects["pc_set"] = target
                    side_effects["branch_taken"] = True
                    side_effects["branch_target"] = target
                    side_effects["branch_type"] = "conditional"
                    
                    # Record control flow event
                    self._record_control_flow(
                        self.registers.get_pc(),
                        target,
                        "conditional_jump",
                        instruction.opcode,
                        True
                    )
                    
                    return False
                else:
                    # Condition is false, don't take the jump
                    side_effects["branch_taken"] = False
                    side_effects["branch_type"] = "conditional"
                    return True  # Increment PC normally
        
        # Handle JGT (Jump if Greater Than)
        elif instruction.opcode == "JGT":
            if len(instruction.operands) >= 2:
                condition_reg = instruction.operands[0]
                target = self._get_operand_value(instruction.operands[1])
                
                # Get the condition value as a signed 32-bit integer
                condition_value = self.registers.get(condition_reg)
                # Convert to signed value if needed (treating as 32-bit signed integer)
                if condition_value > 0x7FFFFFFF:
                    condition_value = condition_value - 0x100000000
                
                if condition_value > 0:
                    # Condition is true, take the jump
                    self.registers.set_pc(target)
                    side_effects["pc_set"] = target
                    side_effects["branch_taken"] = True
                    side_effects["branch_target"] = target
                    side_effects["branch_type"] = "conditional"
                    
                    # Record control flow event
                    self._record_control_flow(
                        self.registers.get_pc(),
                        target,
                        "conditional_jump",
                        instruction.opcode,
                        True
                    )
                    
                    return False
                else:
                    # Condition is false, don't take the jump
                    side_effects["branch_taken"] = False
                    side_effects["branch_type"] = "conditional"
                    return True  # Increment PC normally
        
        # Handle JLT (Jump if Less Than)
        elif instruction.opcode == "JLT":
            if len(instruction.operands) >= 2:
                condition_reg = instruction.operands[0]
                target = self._get_operand_value(instruction.operands[1])
                
                # Get the condition value
                condition_value = self.registers.get(condition_reg)
                
                if condition_value < 0:
                    # Condition is true, take the jump
                    self.registers.set_pc(target)
                    side_effects["pc_set"] = target
                    side_effects["branch_taken"] = True
                    side_effects["branch_target"] = target
                    side_effects["branch_type"] = "conditional"
                    
                    # Record control flow event
                    self._record_control_flow(
                        self.registers.get_pc(),
                        target,
                        "conditional_jump",
                        instruction.opcode,
                        True
                    )
                    
                    return False
                else:
                    # Condition is false, don't take the jump
                    side_effects["branch_taken"] = False
                    side_effects["branch_type"] = "conditional"
                    return True  # Increment PC normally
                    
        # For other branch instructions, use the base implementation
        return super()._execute_branch(instruction, side_effects)
    
    def _execute_system(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> bool:
        """
        Execute a system instruction with parallel VM enhancements.
        
        Args:
            instruction: The system instruction to execute
            side_effects: Dictionary to store side effects
            
        Returns:
            Whether to increment the PC after execution
        """
        # Handle HALT instruction specially for parallel VM
        if instruction.opcode == "HALT":
            # Stop the current thread
            side_effects["halt"] = True
            self.state = ProcessorState.TERMINATED
            
            # Save original PC before incrementing it - ensures we don't
            # re-execute the HALT instruction if the thread is revived
            old_pc = self.registers.get_pc()
            self.registers.set_pc(old_pc + 1)
            
            return False  # Don't increment PC again
            
        # Handle YIELD instruction specially for parallel VM
        elif instruction.opcode == "YIELD":
            # Yield the processor
            side_effects["yield"] = True
            self.state = ProcessorState.WAITING
            
            # Increment PC to move past the YIELD instruction
            old_pc = self.registers.get_pc()
            self.registers.set_pc(old_pc + 1)
            
            return False  # Don't increment PC again
            
        # For other system operations, use the base implementation
        return super()._execute_system(instruction, side_effects)
    
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
                
                # Save original PC before incrementing it
                old_pc = self.registers.get_pc()
                # Increment PC to move to next instruction
                self.registers.set_pc(old_pc + 1)
                side_effects["pc_increment"] = True
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
                
                # Save original PC before incrementing it
                old_pc = self.registers.get_pc()
                # Increment PC to move to next instruction
                self.registers.set_pc(old_pc + 1)
                side_effects["pc_increment"] = True
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        elif instruction.opcode == "BARRIER":
            if len(instruction.operands) >= 1:
                barrier_id = self._get_operand_value(instruction.operands[0])
                side_effects["barrier"] = barrier_id
                
                # Save original PC before incrementing it
                old_pc = self.registers.get_pc()
                # Increment PC to move to next instruction
                self.registers.set_pc(old_pc + 1)
                side_effects["pc_increment"] = True
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        elif instruction.opcode == "JOIN_ALL":
            side_effects["join_all"] = True
            
            # Save original PC before incrementing it
            old_pc = self.registers.get_pc()
            # Increment PC to move to next instruction
            self.registers.set_pc(old_pc + 1)
            side_effects["pc_increment"] = True
        
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