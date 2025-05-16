"""
CPU implementation for the secure VM.

This module implements a simplified CPU architecture with registers, instructions,
and support for different privilege levels and security isolation.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple, Union, Any, Callable
from enum import Enum
import struct
import time

from common.core.processor import (
    Processor as BaseProcessor,
    ProcessorState,
    PrivilegeLevel,
    RegisterSet
)
from common.core.instruction import Instruction, InstructionType
from common.core.exceptions import (
    ProcessorException, InvalidInstructionException, PrivilegeViolationException
)

from secure_vm.memory import Memory, MemoryPermission


# Re-export common types
PrivilegeLevel = PrivilegeLevel


class CPUException(ProcessorException):
    """Base class for CPU execution exceptions."""
    pass


class SegmentationFault(CPUException):
    """Raised when memory access violates segmentation rules."""
    pass


class ProtectionFault(CPUException):
    """Raised when memory access violates protection rules."""
    pass


class InvalidInstruction(CPUException):
    """Raised when attempting to execute an invalid instruction."""
    pass


class PrivilegeViolation(CPUException):
    """Raised when an operation violates privilege restrictions."""
    
    def __init__(self, message: str, required_level: str, current_level: str):
        super().__init__(message)
        self.required_level = required_level
        self.current_level = current_level
    
    def __str__(self) -> str:
        return f"{super().__str__()} (required {self.required_level}, had {self.current_level})"


class InstructionType(Enum):
    """Categories of instruction types for the VM."""
    ARITHMETIC = InstructionType.COMPUTE
    MEMORY = InstructionType.MEMORY
    CONTROL = InstructionType.BRANCH
    SYSTEM = InstructionType.SYSTEM
    SPECIAL = InstructionType.SPECIAL


class ControlFlowRecord:
    """Records a control flow event for integrity monitoring."""
    
    def __init__(
        self,
        from_address: int,
        to_address: int,
        event_type: str,
        instruction: str,
        legitimate: bool = True,
        context: Dict[str, Any] = None,
    ):
        self.from_address = from_address
        self.to_address = to_address
        self.event_type = event_type
        self.instruction = instruction
        self.legitimate = legitimate
        self.context = context or {}
        self.timestamp = time.time()
    
    def __str__(self) -> str:
        return (
            f"Control flow: {self.event_type} from 0x{self.from_address:x} "
            f"to 0x{self.to_address:x} via {self.instruction} "
            f"{'(legitimate)' if self.legitimate else '(HIJACKED)'}"
        )


class CPURegisters(RegisterSet):
    """CPU register state with security-specific extensions."""
    
    def __init__(self, register_count: int = 8):
        """
        Initialize the register set.
        
        Args:
            register_count: Number of general purpose registers
        """
        super().__init__(register_count)
        
        # Explicitly add R0-R7 registers for tests
        for i in range(register_count):
            self.registers[f"R{i}"] = 0
        
        # Aliases for common registers to match secure VM's naming convention
        self.ip = 0       # Instruction pointer
        self.sp = 0       # Stack pointer
        self.bp = 0       # Base pointer
        self.flags = 0    # Flags register
        
        # Protection and privilege registers
        self.privilege_level = PrivilegeLevel.USER
        self.protection_key = 0
    
    def set_ip(self, value: int) -> None:
        """Set the instruction pointer value."""
        self.ip = value & 0xFFFFFFFF
        self.registers["PC"] = self.ip  # Update PC for compatibility
    
    def get_ip(self) -> int:
        """Get the instruction pointer value."""
        return self.ip
    
    def set_sp(self, value: int) -> None:
        """Set the stack pointer value."""
        self.sp = value & 0xFFFFFFFF
        self.registers["SP"] = self.sp  # Update SP for compatibility
    
    def get_sp(self) -> int:
        """Get the stack pointer value."""
        return self.sp
    
    def set_bp(self, value: int) -> None:
        """Set the base pointer value."""
        self.bp = value & 0xFFFFFFFF
        self.registers["FP"] = self.bp  # Update FP for compatibility
    
    def get_bp(self) -> int:
        """Get the base pointer value."""
        return self.bp
    
    def set_flags(self, value: int) -> None:
        """Set the flags register value."""
        self.flags = value & 0xFFFFFFFF
        self.registers["FLAGS"] = self.flags  # Update FLAGS for compatibility
    
    def get_flags(self) -> int:
        """Get the flags register value."""
        return self.flags
    
    # Add compatibility method for tests that use get_register
    def get_register(self, index: int) -> int:
        """Get the value of a register at the given index."""
        # Check index range
        if index < 0 or index >= 8:
            raise ValueError(f"Register index out of range: {index}")
        
        # Map from numeric index to register name
        register_name = f"R{index}"
        
        # Add the register if it doesn't exist (tests might request registers we didn't initialize)
        if register_name not in self.registers:
            self.registers[register_name] = 0
            
        return self.get(register_name)

    # Add compatibility method for tests that use set_register
    def set_register(self, index: int, value: int) -> None:
        """Set the value of a register at the given index."""
        # Check index range
        if index < 0 or index >= 8:
            raise ValueError(f"Register index out of range: {index}")
            
        # Map from numeric index to register name
        register_name = f"R{index}"
        
        # Add the register if it doesn't exist
        if register_name not in self.registers:
            self.registers[register_name] = 0
            
        # Handle 32-bit truncation as required by test
        if value > 0xFFFFFFFF:
            value = value & 0xFFFFFFFF
            
        self.set(register_name, value)
    
    def dump_registers(self) -> Dict[str, int]:
        """Get a snapshot of all register values."""
        result = {f"R{i}": self.get_register(i) for i in range(8)}
        result.update({
            "IP": self.ip,
            "SP": self.sp,
            "BP": self.bp,
            "FLAGS": self.flags,
            "PRIV": self.privilege_level.value,
            "PKEY": self.protection_key,
        })
        return result
    
    def reset(self) -> None:
        """Reset all registers to their initial values."""
        super().reset()
        self.ip = 0
        self.sp = 0
        self.bp = 0
        self.flags = 0
        self.privilege_level = PrivilegeLevel.USER
        self.protection_key = 0


class CPU(BaseProcessor):
    """
    CPU implementation with security-focused features.
    
    This CPU extends the base processor with security features like
    control flow integrity and privilege level enforcement.
    """
    
    # Instruction set definition
    INSTRUCTIONS = {
        # Arithmetic instructions
        0x01: ("ADD", InstructionType.ARITHMETIC, 2),
        0x02: ("SUB", InstructionType.ARITHMETIC, 2),
        0x03: ("MUL", InstructionType.ARITHMETIC, 2),
        0x04: ("DIV", InstructionType.ARITHMETIC, 2),
        
        # Memory instructions
        0x10: ("MOV", InstructionType.MEMORY, 2),
        0x11: ("LOAD", InstructionType.MEMORY, 2),
        0x12: ("STORE", InstructionType.MEMORY, 2),
        0x13: ("PUSH", InstructionType.MEMORY, 1),
        0x14: ("POP", InstructionType.MEMORY, 1),
        
        # Control flow instructions
        0x20: ("JMP", InstructionType.CONTROL, 1),
        0x21: ("JZ", InstructionType.CONTROL, 1),
        0x22: ("JNZ", InstructionType.CONTROL, 1),
        0x23: ("CALL", InstructionType.CONTROL, 1),
        0x24: ("RET", InstructionType.CONTROL, 0),
        
        # System instructions
        0x30: ("SYSCALL", InstructionType.SYSTEM, 1, PrivilegeLevel.USER),  # Can be called from any level
        0x31: ("SYSRET", InstructionType.SYSTEM, 0, PrivilegeLevel.SUPERVISOR),
        0x32: ("ELEVATE", InstructionType.SYSTEM, 1, PrivilegeLevel.KERNEL),
        0x33: ("LOWER", InstructionType.SYSTEM, 1, PrivilegeLevel.USER),  # Can be called from any level
        
        # Special instructions
        0xF0: ("NOP", InstructionType.SPECIAL, 0),
        0xF1: ("HALT", InstructionType.SPECIAL, 0),
        0xF2: ("INT", InstructionType.SPECIAL, 1),
    }
    
    def __init__(self, memory: Memory):
        """
        Initialize the CPU.
        
        Args:
            memory: The memory system to use
        """
        super().__init__(
            processor_id=0,              # Single CPU for security VM
            register_count=8,            # 8 registers for security VM
            privilege_enforcement=True,  # Enable privilege enforcement for security
        )
        
        # Replace standard register set with security-focused one
        self.registers = CPURegisters(8)
        
        # Memory system
        self.memory = memory
        
        # Security and protection state
        self.halted = False
        self.running = False
        self.execution_start_time = 0
        self.execution_time = 0
        self.cycles = 0  # For backward compatibility with tests
        
        # Control flow integrity
        self.control_flow_records: List[ControlFlowRecord] = []
        self.shadow_stack: List[int] = []  # For control flow integrity
        
        # Syscall handling
        self.syscall_table: Dict[int, Callable] = {}
        
        # Register instruction handlers
        self._register_instruction_handlers()
    
    def _register_instruction_handlers(self) -> None:
        """Register instruction handlers for security-specific instructions."""
        # System calls
        self.register_instruction_handler("SYSCALL", self._handle_syscall)
        self.register_instruction_handler("SYSRET", self._handle_sysret)
        self.register_instruction_handler("ELEVATE", self._handle_elevate)
        self.register_instruction_handler("LOWER", self._handle_lower)
        
        # Control flow integrity
        self.register_instruction_handler("CALL", self._handle_call)
        self.register_instruction_handler("RET", self._handle_ret)
    
    def reset(self) -> None:
        """Reset the CPU state."""
        super().reset()
        self.control_flow_records = []
        self.shadow_stack = []
        self.running = False
        self.halted = False
        self.execution_start_time = 0
        self.execution_time = 0
        self.cycles = 0  # Reset cycles for tests
    
    def fetch(self) -> int:
        """
        Fetch the next instruction byte from memory.
        
        Returns:
            The instruction byte
            
        Raises:
            SegmentationFault: If the fetch address is invalid
        """
        try:
            # Try to execute code at this address (enforces DEP)
            instr_byte = self.memory.execute(
                self.registers.get_ip(),
                {"instruction_pointer": self.registers.get_ip()}
            )
            self.registers.set_ip(self.registers.get_ip() + 1)
            return instr_byte
        except Exception as e:
            # Convert memory exceptions to CPU exceptions
            raise SegmentationFault(f"Failed to fetch instruction: {str(e)}")
    
    def fetch_word(self) -> int:
        """
        Fetch a 32-bit word from memory at the instruction pointer.
        
        Returns:
            The 32-bit word
            
        Raises:
            SegmentationFault: If the fetch address is invalid
        """
        try:
            # Read a word from memory
            word = self.memory.read_word(
                self.registers.get_ip(),
                {"instruction_pointer": self.registers.get_ip()}
            )
            self.registers.set_ip(self.registers.get_ip() + 4)
            return word
        except Exception as e:
            # Convert memory exceptions to CPU exceptions
            raise SegmentationFault(f"Failed to fetch word: {str(e)}")
    
    def push(self, value: int) -> None:
        """
        Push a value onto the stack.
        
        Args:
            value: The value to push
            
        Raises:
            SegmentationFault: If the stack operation fails
        """
        try:
            # Adjust stack pointer and write value
            self.registers.set_sp(self.registers.get_sp() - 4)
            self.memory.write_word(
                self.registers.get_sp(),
                value,
                {"instruction_pointer": self.registers.get_ip()}
            )
        except Exception as e:
            # Restore SP if push failed
            self.registers.set_sp(self.registers.get_sp() + 4)
            raise SegmentationFault(f"Failed to push value: {str(e)}")
    
    def pop(self) -> int:
        """
        Pop a value from the stack.
        
        Returns:
            The popped value
            
        Raises:
            SegmentationFault: If the stack operation fails
        """
        try:
            # Read value and adjust stack pointer
            value = self.memory.read_word(
                self.registers.get_sp(),
                {"instruction_pointer": self.registers.get_ip()}
            )
            self.registers.set_sp(self.registers.get_sp() + 4)
            return value
        except Exception as e:
            # Convert memory exceptions to CPU exceptions
            raise SegmentationFault(f"Failed to pop value: {str(e)}")
    
    def _handle_syscall(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Handle a system call instruction.
        
        Args:
            instruction: The syscall instruction
            side_effects: Dictionary to store side effects
            
        Returns:
            (increment_pc, side_effects) tuple
        """
        # Get syscall number from register R0
        syscall_num = self.registers.get(0)
        
        # Record control flow event
        self._record_control_flow(
            self.registers.get_ip() - 1,
            self.registers.get_ip(),
            "syscall",
            f"SYSCALL {syscall_num}",
            True,
            {"syscall_num": syscall_num}
        )
        
        # Store original privilege level
        original_level = self.registers.privilege_level
        
        # Temporarily elevate privilege to execute syscall
        # Syscalls typically run at SUPERVISOR level
        if original_level.value < PrivilegeLevel.SUPERVISOR.value:
            self.registers.privilege_level = PrivilegeLevel.SUPERVISOR
        
        # Execute the syscall if registered
        result = 0
        if syscall_num in self.syscall_table:
            try:
                result = self.syscall_table[syscall_num](self)
            except Exception as e:
                # Record syscall error
                self._record_control_flow(
                    self.registers.get_ip() - 1,
                    self.registers.get_ip(),
                    "syscall_error",
                    f"SYSCALL {syscall_num}",
                    True,
                    {"error": str(e)}
                )
                result = -1
        
        # Store result in R0
        self.registers.set(0, result)
        
        # Add side effect for VM to handle
        side_effects["syscall_executed"] = {
            "number": syscall_num,
            "result": result
        }
        
        return True, side_effects
    
    def _handle_sysret(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Handle a system return instruction.
        
        Args:
            instruction: The sysret instruction
            side_effects: Dictionary to store side effects
            
        Returns:
            (increment_pc, side_effects) tuple
        """
        prev_privilege = self.registers.privilege_level
        
        # Record control flow event
        self._record_control_flow(
            self.registers.get_ip() - 1,
            self.registers.get_ip(),
            "sysret",
            "SYSRET",
            True,
            {"previous_privilege": prev_privilege.name}
        )
        
        # Only lower privilege on return, never elevate
        if prev_privilege.value > PrivilegeLevel.USER.value:
            # Always return to user mode
            self.registers.privilege_level = PrivilegeLevel.USER
        
        # Add side effect for VM to handle
        side_effects["sysret"] = {
            "previous_level": prev_privilege.name,
            "new_level": self.registers.privilege_level.name
        }
        
        return True, side_effects
    
    def _handle_elevate(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Handle a privilege elevation instruction.
        
        Args:
            instruction: The elevate instruction
            side_effects: Dictionary to store side effects
            
        Returns:
            (increment_pc, side_effects) tuple
        """
        # Get target privilege level from register R0
        target_level = self.registers.get(0)
        
        # Check if target level is valid
        if 0 <= target_level <= 2:
            prev_level = self.registers.privilege_level
            self.registers.privilege_level = PrivilegeLevel(target_level)
            
            # Record control flow event
            self._record_control_flow(
                self.registers.get_ip() - 1,
                self.registers.get_ip(),
                "privilege_change",
                "ELEVATE",
                True,
                {
                    "previous_level": prev_level.name,
                    "new_level": self.registers.privilege_level.name
                }
            )
            
            # Add side effect for VM to handle
            side_effects["privilege_change"] = {
                "previous_level": prev_level.name,
                "new_level": self.registers.privilege_level.name
            }
        else:
            # Invalid privilege level
            raise CPUException(f"Invalid privilege level: {target_level}")
        
        return True, side_effects
    
    def _handle_lower(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Handle a privilege lowering instruction.
        
        Args:
            instruction: The lower instruction
            side_effects: Dictionary to store side effects
            
        Returns:
            (increment_pc, side_effects) tuple
        """
        # Get target privilege level from register R0
        target_level = self.registers.get(0)
        current_level = self.registers.privilege_level.value
        
        # Can only lower privilege, not elevate
        if 0 <= target_level < current_level:
            prev_level = self.registers.privilege_level
            self.registers.privilege_level = PrivilegeLevel(target_level)
            
            # Record control flow event
            self._record_control_flow(
                self.registers.get_ip() - 1,
                self.registers.get_ip(),
                "privilege_change",
                "LOWER",
                True,
                {
                    "previous_level": prev_level.name,
                    "new_level": self.registers.privilege_level.name
                }
            )
            
            # Add side effect for VM to handle
            side_effects["privilege_change"] = {
                "previous_level": prev_level.name,
                "new_level": self.registers.privilege_level.name
            }
        else:
            # Invalid privilege level change
            raise PrivilegeViolationException(
                f"Cannot elevate privilege from {current_level} to {target_level}",
                "LOWER",
                str(current_level)
            )
        
        return True, side_effects
    
    def _handle_call(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Handle a call instruction with control flow integrity.
        
        Args:
            instruction: The call instruction
            side_effects: Dictionary to store side effects
            
        Returns:
            (increment_pc, side_effects) tuple
        """
        # Get target address from register R0
        target_reg = 0  # First register contains target
        target = self.registers.get(target_reg)
        return_addr = self.registers.get_ip()
        
        # Record return address in shadow stack for control flow integrity
        self.shadow_stack.append(return_addr)
        
        # Push return address onto the stack
        self.push(return_addr)
        
        # Record the control flow event
        self._record_control_flow(
            self.registers.get_ip() - 1,
            target,
            "call",
            "CALL",
            True
        )
        
        # Set the new PC
        self.registers.set_ip(target)
        
        # Add side effect for VM to handle
        side_effects["call"] = {
            "target": target,
            "return_addr": return_addr
        }
        
        # Don't increment PC
        return False, side_effects
    
    def _handle_ret(
        self,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Handle a return instruction with control flow integrity.
        
        Args:
            instruction: The ret instruction
            side_effects: Dictionary to store side effects
            
        Returns:
            (increment_pc, side_effects) tuple
        """
        # Pop return address from stack
        return_addr = self.pop()
        
        # Control flow integrity check using shadow stack
        shadow_valid = True
        expected_return = None
        
        if self.shadow_stack:
            expected_return = self.shadow_stack.pop()
            if expected_return != return_addr:
                shadow_valid = False
                # Record control flow violation
                self._record_control_flow(
                    self.registers.get_ip() - 1,
                    return_addr,
                    "return",
                    "RET",
                    False,
                    {
                        "expected": expected_return,
                        "actual": return_addr
                    }
                )
        else:
            shadow_valid = False
            # Record control flow violation - shadow stack empty
            self._record_control_flow(
                self.registers.get_ip() - 1,
                return_addr,
                "return",
                "RET",
                False,
                {"error": "Shadow stack empty"}
            )
        
        if shadow_valid:
            # Record legitimate control flow
            self._record_control_flow(
                self.registers.get_ip() - 1,
                return_addr,
                "return",
                "RET",
                True
            )
        
        # Set the new PC
        self.registers.set_ip(return_addr)
        
        # Add side effect for VM to handle
        side_effects["ret"] = {
            "return_addr": return_addr,
            "shadow_valid": shadow_valid,
            "expected_return": expected_return
        }
        
        # Don't increment PC
        return False, side_effects
    
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
        Record a control flow event for integrity monitoring.
        
        Args:
            from_address: Source address
            to_address: Destination address
            event_type: Type of control flow event
            instruction: Instruction that caused the event
            legitimate: Whether the control flow is legitimate
            context: Additional context for the event
        """
        record = ControlFlowRecord(
            from_address=from_address,
            to_address=to_address,
            event_type=event_type,
            instruction=instruction,
            legitimate=legitimate,
            context=context,
        )
        self.control_flow_records.append(record)
    
    def register_syscall(self, syscall_num: int, handler: Callable) -> None:
        """
        Register a system call handler.
        
        Args:
            syscall_num: The syscall number
            handler: Function to handle the syscall
        """
        self.syscall_table[syscall_num] = handler
    
    def decode_instruction(self, opcode: int) -> Tuple[str, InstructionType, int, Optional[PrivilegeLevel]]:
        """
        Decode an instruction opcode.
        
        Args:
            opcode: The instruction opcode
            
        Returns:
            Tuple of (name, type, operand_count, required_privilege)
            
        Raises:
            InvalidInstruction: If the opcode is invalid
        """
        if opcode not in self.INSTRUCTIONS:
            raise InvalidInstruction(f"Invalid opcode: 0x{opcode:02x}")
        
        instruction_info = self.INSTRUCTIONS[opcode]
        
        name = instruction_info[0]
        instr_type = instruction_info[1]
        operand_count = instruction_info[2]
        
        # Get required privilege if specified
        required_privilege = None
        if len(instruction_info) > 3:
            required_privilege = instruction_info[3]
        
        return name, instr_type, operand_count, required_privilege
    
    def run(self, max_instructions: int = 10000) -> int:
        """
        Run the CPU for up to max_instructions.
        
        Args:
            max_instructions: Maximum number of instructions to execute
            
        Returns:
            Number of instructions executed
        """
        if self.halted:
            return 0
        
        self.running = True
        self.execution_start_time = time.time()
        instructions_executed = 0
        
        try:
            while self.running and instructions_executed < max_instructions:
                # Fetch instruction
                opcode = self.fetch()
                
                # Get instruction info
                name, instr_type, operand_count, required_privilege = self.decode_instruction(opcode)
                
                # Check privilege if required
                if (required_privilege is not None and 
                        self.registers.privilege_level.value < required_privilege.value):
                    # Record privilege violation
                    self._record_control_flow(
                        self.registers.get_ip() - 1,
                        self.registers.get_ip(),
                        "privilege_violation",
                        name,
                        False,
                        {
                            "required": required_privilege.name,
                            "current": self.registers.privilege_level.name
                        }
                    )
                    raise PrivilegeViolationException(
                        f"Insufficient privilege for instruction {name}",
                        required_privilege.name,
                        self.registers.privilege_level.name
                    )
                
                # Create instruction object from decoded info
                instruction = Instruction(
                    opcode=name,
                    type=instr_type,
                    operands=[f"R{i}" for i in range(operand_count)],
                    privileged=(required_privilege is not None and 
                               required_privilege.value > PrivilegeLevel.USER.value)
                )
                
                # Execute instruction with control flow recording
                completed, side_effects = self.execute_instruction(instruction)
                
                # Process side effects from execution
                if not completed:
                    # Skip handling side effects until instruction completes
                    pass
                
                # Handle special instructions like HALT
                if "halt" in side_effects:
                    self.halted = True
                    self.running = False
                    break
                
                instructions_executed += 1
        
        except Exception as e:
            self.running = False
            # Record the exception
            self._record_control_flow(
                self.registers.get_ip(),
                0,
                "exception",
                str(e),
                False
            )
        
        finally:
            self.execution_time += time.time() - self.execution_start_time
        
        return instructions_executed
    
    def get_control_flow_trace(self) -> List[ControlFlowRecord]:
        """
        Get the control flow trace for visualization.
        
        Returns:
            List of control flow records
        """
        return self.control_flow_records
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for the CPU.
        
        Returns:
            Dictionary of performance statistics
        """
        return {
            "cycles": self.cycle_count,
            "execution_time": self.execution_time,
            "instructions_per_second": self.cycle_count / max(self.execution_time, 0.001),
            "control_flow_events": len(self.control_flow_records),
        }