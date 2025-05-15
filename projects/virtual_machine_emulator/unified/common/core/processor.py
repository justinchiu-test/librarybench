"""
Processor implementation for virtual machine emulators.

This module provides a common processor implementation that can be
used by both the security-focused and parallel computing-focused VM implementations.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Any, Callable

from common.core.instruction import Instruction, InstructionType
from common.core.exceptions import (
    ProcessorException, InvalidInstructionException, PrivilegeViolationException
)


class ProcessorState(Enum):
    """States that a processor can be in."""
    IDLE = auto()       # Processor not running any thread
    RUNNING = auto()    # Actively executing instructions
    WAITING = auto()    # Waiting on synchronization primitive
    BLOCKED = auto()    # Blocked on I/O or similar
    TERMINATED = auto() # Thread terminated


class PrivilegeLevel(Enum):
    """Privilege levels for processor execution."""
    USER = 0         # Unprivileged user code
    SUPERVISOR = 1   # Limited system operations
    KERNEL = 2       # Full system access
    
    def __lt__(self, other):
        if isinstance(other, PrivilegeLevel):
            return self.value < other.value
        return NotImplemented
    
    def __gt__(self, other):
        if isinstance(other, PrivilegeLevel):
            return self.value > other.value
        return NotImplemented
    
    def __le__(self, other):
        if isinstance(other, PrivilegeLevel):
            return self.value <= other.value
        return NotImplemented
    
    def __ge__(self, other):
        if isinstance(other, PrivilegeLevel):
            return self.value >= other.value
        return NotImplemented


class RegisterSet:
    """Registry implementation for the processor."""
    
    def __init__(
        self,
        general_registers: int = 16,
        use_numeric_names: bool = False
    ):
        """
        Initialize the register set.
        
        Args:
            general_registers: Number of general-purpose registers
            use_numeric_names: Whether to use numeric names (R0, R1) or 
                               named registers (A, B, AX, BX)
        """
        # Initialize general purpose registers
        self.registers: Dict[str, int] = {}
        
        if use_numeric_names:
            # R0-RN style registers
            for i in range(general_registers):
                self.registers[f"R{i}"] = 0
        else:
            # Use named registers based on the number requested
            if general_registers >= 2:
                self.registers.update({
                    "A": 0, "B": 0
                })
            if general_registers >= 4:
                self.registers.update({
                    "C": 0, "D": 0
                })
            if general_registers >= 8:
                self.registers.update({
                    "E": 0, "F": 0, "G": 0, "H": 0
                })
            if general_registers >= 16:
                self.registers.update({
                    "I": 0, "J": 0, "K": 0, "L": 0, 
                    "M": 0, "N": 0, "O": 0, "P": 0
                })
        
        # Add special registers
        self.registers.update({
            "PC": 0,      # Program counter
            "SP": 0,      # Stack pointer
            "FP": 0,      # Frame pointer
            "FLAGS": 0,   # Status flags
        })
        
        # State registers
        self.privilege_level = PrivilegeLevel.USER
        
        # Flag bit positions
        self.FLAG_ZERO = 0        # Zero result
        self.FLAG_NEGATIVE = 1    # Negative result
        self.FLAG_CARRY = 2       # Carry out
        self.FLAG_OVERFLOW = 3    # Arithmetic overflow
        self.FLAG_INTERRUPT = 4   # Interrupts enabled/disabled
    
    def get(self, register: str) -> int:
        """
        Get the value of a register.
        
        Args:
            register: The register name
            
        Returns:
            The register value
            
        Raises:
            KeyError: If the register doesn't exist
        """
        if register not in self.registers:
            raise KeyError(f"Unknown register: {register}")
        return self.registers[register]
    
    def set(self, register: str, value: int) -> None:
        """
        Set the value of a register.
        
        Args:
            register: The register name
            value: The value to set
            
        Raises:
            KeyError: If the register doesn't exist
        """
        if register not in self.registers:
            raise KeyError(f"Unknown register: {register}")
        self.registers[register] = value & 0xFFFFFFFF  # 32-bit registers
    
    def get_pc(self) -> int:
        """Get the program counter value."""
        return self.registers["PC"]
    
    def set_pc(self, value: int) -> None:
        """Set the program counter value."""
        self.registers["PC"] = value & 0xFFFFFFFF
    
    def set_flag(self, flag_position: int, value: bool) -> None:
        """
        Set or clear a specific flag bit.
        
        Args:
            flag_position: The bit position of the flag
            value: True to set, False to clear
        """
        if value:
            self.registers["FLAGS"] |= (1 << flag_position)
        else:
            self.registers["FLAGS"] &= ~(1 << flag_position)
    
    def get_flag(self, flag_position: int) -> bool:
        """
        Get the value of a specific flag bit.
        
        Args:
            flag_position: The bit position of the flag
            
        Returns:
            True if the flag is set, False otherwise
        """
        return (self.registers["FLAGS"] & (1 << flag_position)) != 0
    
    def dump(self) -> Dict[str, Any]:
        """
        Get a snapshot of all register values.
        
        Returns:
            Dictionary of register values and processor state
        """
        result = self.registers.copy()
        result["PRIVILEGE"] = self.privilege_level.name
        return result
    
    def reset(self) -> None:
        """Reset all registers to their initial values."""
        for register in self.registers:
            self.registers[register] = 0
        self.privilege_level = PrivilegeLevel.USER


class Processor:
    """
    Base processor implementation for virtual machine emulators.
    
    This class provides core functionality for instruction execution,
    register management, and processor state tracking.
    """
    
    def __init__(
        self,
        processor_id: int,
        register_count: int = 16,
        privilege_enforcement: bool = True
    ):
        """
        Initialize the processor.
        
        Args:
            processor_id: Unique identifier for this processor
            register_count: Number of general purpose registers
            privilege_enforcement: Whether to enforce privilege levels
        """
        self.processor_id = processor_id
        self.registers = RegisterSet(register_count)
        self.state = ProcessorState.IDLE
        self.current_thread_id: Optional[str] = None
        self.cycle_count = 0
        self.stall_cycles = 0  # Cycles remaining for current instruction
        self.privilege_enforcement = privilege_enforcement
        
        # Execution context
        self.instruction_handlers: Dict[str, Callable] = {}
        self.control_flow_records: List[Dict[str, Any]] = []
        
        # Default register for instruction handlers (convention)
        self.register_convention = {
            "accumulator": "A" if register_count >= 2 else "R0",
            "counter": "C" if register_count >= 4 else "R2",
            "data": "D" if register_count >= 4 else "R3",
            "result": "A" if register_count >= 2 else "R0"
        }
    
    def reset(self) -> None:
        """Reset the processor to its initial state."""
        self.registers.reset()
        self.state = ProcessorState.IDLE
        self.current_thread_id = None
        self.cycle_count = 0
        self.stall_cycles = 0
        self.control_flow_records = []
    
    def is_busy(self) -> bool:
        """
        Check if the processor is busy.
        
        Returns:
            True if the processor is busy, False otherwise
        """
        return self.state != ProcessorState.IDLE
    
    def register_instruction_handler(
        self,
        opcode: str,
        handler: Callable
    ) -> None:
        """
        Register a custom handler for an instruction.
        
        Args:
            opcode: The instruction opcode to handle
            handler: Function to handle the instruction
        """
        self.instruction_handlers[opcode] = handler
    
    def start_thread(
        self,
        thread_id: str,
        pc: int,
        initial_registers: Optional[Dict[str, int]] = None
    ) -> None:
        """
        Start a thread running on this processor.
        
        Args:
            thread_id: Identifier for the thread
            pc: Initial program counter value
            initial_registers: Initial register values
        """
        self.current_thread_id = thread_id
        self.state = ProcessorState.RUNNING
        self.registers.set_pc(pc)
        self.stall_cycles = 0
        
        # Copy initial register values if provided
        if initial_registers:
            for register, value in initial_registers.items():
                if register in self.registers.registers:
                    self.registers.set(register, value)
    
    def execute_instruction(
        self,
        instruction: Instruction
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Execute a single instruction.
        
        Args:
            instruction: The instruction to execute
            
        Returns:
            Tuple of (completed, side_effects):
            - completed: Whether the instruction completed execution
            - side_effects: Dictionary of side effects for the VM to handle
            
        Raises:
            InvalidInstructionException: If the instruction is invalid
            PrivilegeViolationException: If the instruction requires higher privilege
        """
        # Check if instruction is still stalled
        if self.stall_cycles > 0:
            self.stall_cycles -= 1
            return (False, None)
        
        # Check privilege if required
        if (self.privilege_enforcement and instruction.privileged and 
            self.registers.privilege_level != PrivilegeLevel.KERNEL):
            raise PrivilegeViolationException(
                f"Insufficient privilege for instruction {instruction.opcode}",
                "KERNEL",
                self.registers.privilege_level.name
            )
        
        # Set initial stall cycles based on instruction latency
        self.stall_cycles = instruction.latency - 1
        
        # Track cycle count
        self.cycle_count += 1
        
        # Default is to increment PC after execution
        increment_pc = True
        side_effects = {}
        
        # Check if there's a custom handler for this instruction
        if instruction.opcode in self.instruction_handlers:
            # Use the custom handler
            result = self.instruction_handlers[instruction.opcode](
                self, instruction, side_effects
            )
            if isinstance(result, tuple) and len(result) == 2:
                increment_pc, side_effects = result
            elif isinstance(result, dict):
                side_effects = result
            elif isinstance(result, bool):
                increment_pc = result
        else:
            # Use generic execution based on instruction type
            if instruction.type == InstructionType.COMPUTE:
                self._execute_compute(instruction, side_effects)
            elif instruction.type == InstructionType.MEMORY:
                self._execute_memory(instruction, side_effects)
            elif instruction.type == InstructionType.BRANCH:
                increment_pc = self._execute_branch(instruction, side_effects)
            elif instruction.type == InstructionType.SYNC:
                self._execute_sync(instruction, side_effects)
            elif instruction.type == InstructionType.SYSTEM:
                increment_pc = self._execute_system(instruction, side_effects)
            elif instruction.type == InstructionType.SPECIAL:
                increment_pc = self._execute_special(instruction, side_effects)
            else:
                raise InvalidInstructionException(
                    f"Unsupported instruction type: {instruction.type}",
                    None, self.registers.get_pc()
                )
        
        # Increment PC if needed
        if increment_pc:
            self.registers.set_pc(self.registers.get_pc() + 1)
        
        # Instruction completes if stall cycles are done
        completed = (self.stall_cycles == 0)
        
        return (completed, side_effects)
    
    def _execute_compute(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> None:
        """
        Execute a compute instruction.
        
        Args:
            instruction: The instruction to execute
            side_effects: Dictionary to store side effects
        """
        # Handle different compute operations
        if len(instruction.operands) < 1:
            raise InvalidInstructionException(
                f"Invalid operand count for {instruction.opcode}",
                None, self.registers.get_pc()
            )
        
        # Default handler for arithmetic operations with dest, src1, src2
        if instruction.opcode in ("ADD", "SUB", "MUL", "DIV", "AND", "OR", "XOR", "SHL", "SHR"):
            if len(instruction.operands) >= 3:
                dest_reg = instruction.operands[0]
                src1_val = self._get_operand_value(instruction.operands[1])
                src2_val = self._get_operand_value(instruction.operands[2])
                
                # Perform the operation
                if instruction.opcode == "ADD":
                    result = src1_val + src2_val
                elif instruction.opcode == "SUB":
                    result = src1_val - src2_val
                elif instruction.opcode == "MUL":
                    result = src1_val * src2_val
                elif instruction.opcode == "DIV":
                    if src2_val == 0:
                        raise ProcessorException("Division by zero")
                    result = src1_val // src2_val
                elif instruction.opcode == "AND":
                    result = src1_val & src2_val
                elif instruction.opcode == "OR":
                    result = src1_val | src2_val
                elif instruction.opcode == "XOR":
                    result = src1_val ^ src2_val
                elif instruction.opcode == "SHL":
                    result = src1_val << src2_val
                elif instruction.opcode == "SHR":
                    result = src1_val >> src2_val
                
                # Set the result
                self.registers.set(dest_reg, result)
                
                # Update flags
                self.registers.set_flag(self.registers.FLAG_ZERO, result == 0)
                self.registers.set_flag(self.registers.FLAG_NEGATIVE, result < 0)
                
                # Record modified registers in side effects
                side_effects["registers_modified"] = [dest_reg]
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        # Other compute operations would be implemented similarly
    
    def _execute_memory(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> None:
        """
        Execute a memory instruction.
        
        Args:
            instruction: The instruction to execute
            side_effects: Dictionary to store side effects
        """
        if instruction.opcode == "LOAD":
            if len(instruction.operands) >= 2:
                dest_reg = instruction.operands[0]
                addr_operand = instruction.operands[1]
                
                # Check if this is a register or immediate address
                if isinstance(addr_operand, int) or (isinstance(addr_operand, str) and addr_operand.isdigit()):
                    # Immediate address
                    addr = self._get_operand_value(addr_operand)
                    side_effects["memory_read"] = addr
                    side_effects["registers_modified"] = [dest_reg]
                elif isinstance(addr_operand, str) and addr_operand in self.registers.registers:
                    # Register containing address
                    addr = self.registers.get(addr_operand)
                    side_effects["memory_read"] = addr
                    side_effects["registers_modified"] = [dest_reg]
                else:
                    # Immediate value load
                    value = self._get_operand_value(addr_operand)
                    self.registers.set(dest_reg, value)
                    side_effects["registers_modified"] = [dest_reg]
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        elif instruction.opcode == "STORE":
            if len(instruction.operands) >= 2:
                src_reg = instruction.operands[0]
                addr_operand = instruction.operands[1]
                
                # Get the value to store
                value = self.registers.get(src_reg)
                
                # Get the address to store to
                addr = self._get_operand_value(addr_operand)
                
                # Create the side effect for the VM to handle
                side_effects["memory_write"] = (addr, value)
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        elif instruction.opcode == "PUSH":
            if len(instruction.operands) >= 1:
                src_reg = instruction.operands[0]
                value = self.registers.get(src_reg)
                
                # Decrement SP
                sp = self.registers.get("SP") - 4
                self.registers.set("SP", sp)
                
                # Store value at stack pointer
                side_effects["memory_write"] = (sp, value)
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        elif instruction.opcode == "POP":
            if len(instruction.operands) >= 1:
                dest_reg = instruction.operands[0]
                
                # Get current SP
                sp = self.registers.get("SP")
                
                # Read from stack pointer
                side_effects["memory_read"] = sp
                side_effects["registers_modified"] = [dest_reg]
                
                # Increment SP
                self.registers.set("SP", sp + 4)
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
    
    def _execute_branch(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> bool:
        """
        Execute a branch instruction.
        
        Args:
            instruction: The instruction to execute
            side_effects: Dictionary to store side effects
            
        Returns:
            Whether to increment the PC after execution
        """
        if instruction.opcode == "JMP":
            if len(instruction.operands) >= 1:
                target = self._get_operand_value(instruction.operands[0])
                
                # Record control flow event
                self._record_control_flow(
                    self.registers.get_pc(),
                    target,
                    "jump",
                    instruction.opcode,
                    True
                )
                
                # Set the new PC
                self.registers.set_pc(target)
                
                # Don't increment PC
                return False
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        elif instruction.opcode == "JZ":
            if len(instruction.operands) >= 2:
                condition_reg = instruction.operands[0]
                target = self._get_operand_value(instruction.operands[1])
                
                if self.registers.get(condition_reg) == 0:
                    # Record control flow event
                    self._record_control_flow(
                        self.registers.get_pc(),
                        target,
                        "conditional_jump",
                        instruction.opcode,
                        True
                    )
                    
                    # Set the new PC
                    self.registers.set_pc(target)
                    
                    # Don't increment PC
                    return False
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        elif instruction.opcode == "JNZ":
            if len(instruction.operands) >= 2:
                condition_reg = instruction.operands[0]
                target = self._get_operand_value(instruction.operands[1])
                
                if self.registers.get(condition_reg) != 0:
                    # Record control flow event
                    self._record_control_flow(
                        self.registers.get_pc(),
                        target,
                        "conditional_jump",
                        instruction.opcode,
                        True
                    )
                    
                    # Set the new PC
                    self.registers.set_pc(target)
                    
                    # Don't increment PC
                    return False
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        elif instruction.opcode == "CALL":
            if len(instruction.operands) >= 1:
                target = self._get_operand_value(instruction.operands[0])
                return_addr = self.registers.get_pc() + 1
                
                # Push return address onto stack
                sp = self.registers.get("SP") - 4
                self.registers.set("SP", sp)
                side_effects["memory_write"] = (sp, return_addr)
                
                # Record control flow event
                self._record_control_flow(
                    self.registers.get_pc(),
                    target,
                    "call",
                    instruction.opcode,
                    True
                )
                
                # Set the new PC
                self.registers.set_pc(target)
                
                # Don't increment PC
                return False
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        elif instruction.opcode == "RET":
            # Get return address from stack
            sp = self.registers.get("SP")
            side_effects["memory_read"] = sp
            
            # Set up side effect to retrieve return address
            side_effects["return"] = True
            
            # Will increment SP after memory read is handled
            self.registers.set("SP", sp + 4)
            
            # PC will be set by VM after memory read
            return True
        
        return True  # Default to incrementing PC
    
    def _execute_sync(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> None:
        """
        Execute a synchronization instruction.
        
        Args:
            instruction: The instruction to execute
            side_effects: Dictionary to store side effects
        """
        if instruction.opcode == "LOCK":
            if len(instruction.operands) >= 1:
                lock_id = self._get_operand_value(instruction.operands[0])
                side_effects["sync_lock"] = lock_id
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        elif instruction.opcode == "UNLOCK":
            if len(instruction.operands) >= 1:
                lock_id = self._get_operand_value(instruction.operands[0])
                side_effects["sync_unlock"] = lock_id
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        elif instruction.opcode == "FENCE":
            # Memory fence ensures visibility of all memory operations
            side_effects["memory_fence"] = True
        
        elif instruction.opcode == "CAS":
            if len(instruction.operands) >= 4:
                addr = self._get_operand_value(instruction.operands[0])
                expected = self._get_operand_value(instruction.operands[1])
                new_value = self._get_operand_value(instruction.operands[2])
                result_reg = instruction.operands[3]
                
                side_effects["cas_operation"] = (addr, expected, new_value, result_reg)
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
    
    def _execute_system(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> bool:
        """
        Execute a system instruction.
        
        Args:
            instruction: The instruction to execute
            side_effects: Dictionary to store side effects
            
        Returns:
            Whether to increment the PC after execution
        """
        if instruction.opcode == "HALT":
            # Stop the current thread
            side_effects["halt"] = True
            self.state = ProcessorState.TERMINATED
            return True
        
        elif instruction.opcode == "YIELD":
            # Voluntarily yield the processor
            side_effects["yield"] = True
            self.state = ProcessorState.WAITING
            return True
        
        elif instruction.opcode == "SYSCALL":
            if len(instruction.operands) >= 1:
                syscall_num = self._get_operand_value(instruction.operands[0])
                side_effects["syscall"] = syscall_num
                
                # Record control flow event
                self._record_control_flow(
                    self.registers.get_pc(),
                    self.registers.get_pc() + 1,
                    "syscall",
                    f"{instruction.opcode} {syscall_num}",
                    True,
                    {"syscall_num": syscall_num}
                )
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        return True  # Default to incrementing PC
    
    def _execute_special(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> bool:
        """
        Execute a special instruction.
        
        Args:
            instruction: The instruction to execute
            side_effects: Dictionary to store side effects
            
        Returns:
            Whether to increment the PC after execution
        """
        if instruction.opcode == "NOP":
            # No operation
            pass
        
        elif instruction.opcode == "SPAWN":
            if len(instruction.operands) >= 3:
                func_addr = self._get_operand_value(instruction.operands[0])
                arg_addr = self._get_operand_value(instruction.operands[1])
                result_reg = instruction.operands[2]
                
                side_effects["spawn_thread"] = (func_addr, arg_addr, result_reg)
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        elif instruction.opcode == "JOIN":
            if len(instruction.operands) >= 1:
                thread_id = self._get_operand_value(instruction.operands[0])
                side_effects["join_thread"] = thread_id
                self.state = ProcessorState.WAITING
            else:
                raise InvalidInstructionException(
                    f"Not enough operands for {instruction.opcode}",
                    None, self.registers.get_pc()
                )
        
        return True  # Default to incrementing PC
    
    def _get_operand_value(self, operand: Any) -> int:
        """
        Get the value of an operand.
        
        Args:
            operand: The operand, either a register name or immediate value
            
        Returns:
            The value of the operand
        """
        if isinstance(operand, str) and operand in self.registers.registers:
            return self.registers.get(operand)
        return int(operand)
    
    def _record_control_flow(
        self,
        from_address: int,
        to_address: int,
        event_type: str,
        instruction: str,
        legitimate: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a control flow event.
        
        Args:
            from_address: Source address
            to_address: Destination address
            event_type: Type of control flow event
            instruction: Instruction that caused the control flow
            legitimate: Whether the control flow is legitimate
            context: Additional context
        """
        record = {
            "from_address": from_address,
            "to_address": to_address,
            "event_type": event_type,
            "instruction": instruction,
            "legitimate": legitimate,
            "timestamp": self.cycle_count,
            "context": context or {}
        }
        self.control_flow_records.append(record)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get processor statistics.
        
        Returns:
            Dictionary of processor statistics
        """
        return {
            "processor_id": self.processor_id,
            "state": self.state.name,
            "cycle_count": self.cycle_count,
            "current_thread": self.current_thread_id,
            "control_flow_events": len(self.control_flow_records),
            "pc": self.registers.get_pc(),
            "privilege_level": self.registers.privilege_level.name
        }