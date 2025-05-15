"""
Attack vectors for the virtual machine emulator.

This module implements various attack techniques for educational purposes:
- Buffer overflow attacks
- Return-Oriented Programming (ROP)
- Format string attacks
- Code injection attacks
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Union, Any, Callable

from common.core.memory import MemorySystem, MemorySegment, MemoryPermission
from common.extensions.security.vulnerability_detection import VulnerabilityType, VulnerabilityInjector


class AttackType(Enum):
    """Types of attack vectors."""
    BUFFER_OVERFLOW = auto()        # Buffer overflow attack
    ROP = auto()                    # Return-oriented programming attack
    FORMAT_STRING = auto()          # Format string attack
    CODE_INJECTION = auto()         # Code injection attack
    ARBITRARY_WRITE = auto()        # Arbitrary memory write attack
    CONTROL_FLOW_HIJACK = auto()    # Control flow hijack attack
    RETURN_TO_LIBC = auto()         # Return-to-libc attack
    HEAP_OVERFLOW = auto()          # Heap overflow attack


class AttackResult:
    """Result of an attack execution."""
    
    def __init__(
        self,
        success: bool,
        attack_type: AttackType,
        details: Dict[str, Any] = None,
        error: Optional[str] = None
    ):
        """
        Initialize an attack result.
        
        Args:
            success: Whether the attack was successful
            attack_type: Type of attack
            details: Attack details
            error: Error message if attack failed
        """
        self.success = success
        self.attack_type = attack_type
        self.details = details or {}
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary."""
        result = {
            "success": self.success,
            "attack_type": self.attack_type.name,
            "details": self.details,
        }
        
        if self.error:
            result["error"] = self.error
        
        return result
    
    def __str__(self) -> str:
        """Return a string representation of the attack result."""
        status = "Success" if self.success else "Failed"
        result = f"{self.attack_type.name} attack: {status}"
        
        if self.error:
            result += f" - {self.error}"
        
        if self.details and len(self.details) > 0:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            result += f" ({details_str})"
        
        return result


class Attack:
    """Base class for attacks."""
    
    def __init__(self, memory: MemorySystem):
        """
        Initialize the attack.
        
        Args:
            memory: Memory system to attack
        """
        self.memory = memory
        self.vulnerability_injector = VulnerabilityInjector(memory)
    
    def execute(self) -> AttackResult:
        """
        Execute the attack.
        
        Returns:
            Result of the attack
        """
        raise NotImplementedError("Attack subclasses must implement execute method")


class BufferOverflowAttack(Attack):
    """Buffer overflow attack implementation."""
    
    def __init__(
        self,
        memory: MemorySystem,
        buffer_address: int,
        buffer_size: int,
        target_address: int,
        payload: Optional[bytes] = None
    ):
        """
        Initialize a buffer overflow attack.
        
        Args:
            memory: Memory system to attack
            buffer_address: Address of the buffer to overflow
            buffer_size: Size of the buffer
            target_address: Target address to overwrite (often a return address)
            payload: Optional custom payload
        """
        super().__init__(memory)
        self.buffer_address = buffer_address
        self.buffer_size = buffer_size
        self.target_address = target_address
        self.payload = payload
    
    def execute(self) -> AttackResult:
        """
        Execute the buffer overflow attack.
        
        Returns:
            Result of the attack
        """
        try:
            # Find the segment containing the buffer
            segment = self.memory.find_segment(self.buffer_address)
            if segment is None:
                return AttackResult(
                    success=False,
                    attack_type=AttackType.BUFFER_OVERFLOW,
                    error=f"Buffer address 0x{self.buffer_address:08x} not in any memory segment"
                )
            
            # Calculate offset to target
            target_segment = self.memory.find_segment(self.target_address)
            if target_segment is None:
                return AttackResult(
                    success=False,
                    attack_type=AttackType.BUFFER_OVERFLOW,
                    error=f"Target address 0x{self.target_address:08x} not in any memory segment"
                )
            
            # Create the overflow payload
            if self.payload is None:
                # Calculate distance to target
                offset = self.target_address - self.buffer_address
                
                # Create a basic overflow payload
                if offset > self.buffer_size:
                    # Fill buffer and continue to target
                    payload = bytes([0x41] * offset)  # 'A's
                    
                    # Overwrite target with a specific value (e.g., shellcode address)
                    payload += (0xDEADBEEF).to_bytes(4, byteorder='little')
                else:
                    # Create payload that fills buffer and overflows
                    payload = bytes([0x41] * self.buffer_size)  # 'A's
                    overflow_size = 32  # Additional bytes beyond buffer
                    payload += bytes([0x42] * (overflow_size - 4))  # 'B's
                    
                    # Overwrite target with a specific value
                    payload += (0xDEADBEEF).to_bytes(4, byteorder='little')
            else:
                payload = self.payload
            
            # Perform the buffer overflow
            result = self.vulnerability_injector.inject_buffer_overflow(
                self.buffer_address,
                len(payload),
                payload
            )
            
            if not result["success"]:
                return AttackResult(
                    success=False,
                    attack_type=AttackType.BUFFER_OVERFLOW,
                    error=result["error"]
                )
            
            # Verify target was overwritten if possible
            try:
                target_value = self.memory.read_word(self.target_address, {"operation": "verify_attack"})
                
                return AttackResult(
                    success=True,
                    attack_type=AttackType.BUFFER_OVERFLOW,
                    details={
                        "buffer_address": self.buffer_address,
                        "buffer_size": self.buffer_size,
                        "target_address": self.target_address,
                        "target_value": target_value,
                        "payload_size": len(payload)
                    }
                )
            except:
                # Can't verify target value, but attack was executed
                return AttackResult(
                    success=True,
                    attack_type=AttackType.BUFFER_OVERFLOW,
                    details={
                        "buffer_address": self.buffer_address,
                        "buffer_size": self.buffer_size,
                        "target_address": self.target_address,
                        "payload_size": len(payload),
                        "verification": "failed"
                    }
                )
        except Exception as e:
            return AttackResult(
                success=False,
                attack_type=AttackType.BUFFER_OVERFLOW,
                error=str(e)
            )


class CodeInjectionAttack(Attack):
    """Code injection attack implementation."""
    
    def __init__(
        self,
        memory: MemorySystem,
        code_address: int,
        shellcode: Optional[bytes] = None,
        entry_point: Optional[int] = None,
    ):
        """
        Initialize a code injection attack.
        
        Args:
            memory: Memory system to attack
            code_address: Address where to inject the shellcode
            shellcode: Optional custom shellcode
            entry_point: Optional entry point to redirect execution
        """
        super().__init__(memory)
        self.code_address = code_address
        self.shellcode = shellcode
        self.entry_point = entry_point
    
    def execute(self) -> AttackResult:
        """
        Execute the code injection attack.
        
        Returns:
            Result of the attack
        """
        try:
            # Find the segment containing the code address
            segment = self.memory.find_segment(self.code_address)
            if segment is None:
                return AttackResult(
                    success=False,
                    attack_type=AttackType.CODE_INJECTION,
                    error=f"Code address 0x{self.code_address:08x} not in any memory segment"
                )
            
            # Default shellcode if none provided (simple infinite loop)
            if self.shellcode is None:
                # Simple x86 shellcode: JMP $ (infinite loop)
                self.shellcode = bytes([0xEB, 0xFE])
            
            # Inject the shellcode
            result = self.vulnerability_injector.inject_code_execution(
                self.code_address,
                len(self.shellcode),
                self.shellcode
            )
            
            if not result["success"]:
                return AttackResult(
                    success=False,
                    attack_type=AttackType.CODE_INJECTION,
                    error=result["error"]
                )
            
            # Redirect execution if entry point provided
            if self.entry_point is not None:
                # Find a way to redirect execution
                # This depends on the VM architecture and available attack vectors
                # For example, we might overwrite a return address or function pointer
                
                try:
                    # Try to inject a JMP instruction to our shellcode
                    # This is architecture-specific (x86 in this example)
                    jmp_instruction = bytes([0xE9])  # JMP rel32
                    offset = (self.code_address - self.entry_point - 5)  # 5 is the size of JMP rel32
                    jmp_instruction += offset.to_bytes(4, byteorder='little', signed=True)
                    
                    # Write the jump instruction
                    self.memory.write_bytes(
                        self.entry_point,
                        jmp_instruction,
                        {"attack": "code_redirection"}
                    )
                    
                    return AttackResult(
                        success=True,
                        attack_type=AttackType.CODE_INJECTION,
                        details={
                            "code_address": self.code_address,
                            "shellcode_size": len(self.shellcode),
                            "entry_point": self.entry_point,
                            "redirection": "jump"
                        }
                    )
                except Exception as e:
                    # Couldn't redirect execution, but shellcode is in place
                    return AttackResult(
                        success=True,
                        attack_type=AttackType.CODE_INJECTION,
                        details={
                            "code_address": self.code_address,
                            "shellcode_size": len(self.shellcode),
                            "redirection": "failed",
                            "redirection_error": str(e)
                        }
                    )
            
            # No redirection needed
            return AttackResult(
                success=True,
                attack_type=AttackType.CODE_INJECTION,
                details={
                    "code_address": self.code_address,
                    "shellcode_size": len(self.shellcode),
                    "segment_name": segment.name if hasattr(segment, 'name') else "unknown"
                }
            )
        except Exception as e:
            return AttackResult(
                success=False,
                attack_type=AttackType.CODE_INJECTION,
                error=str(e)
            )


class ROPAttack(Attack):
    """Return-Oriented Programming (ROP) attack."""
    
    def __init__(
        self,
        memory: MemorySystem,
        stack_address: int,
        gadgets: List[Tuple[int, str]],
        overflow_size: int = 64,
    ):
        """
        Initialize a ROP attack.
        
        Args:
            memory: Memory system to attack
            stack_address: Address of the stack to modify
            gadgets: List of (address, description) tuples for ROP gadgets
            overflow_size: Size of buffer overflow to reach the return address
        """
        super().__init__(memory)
        self.stack_address = stack_address
        self.gadgets = gadgets
        self.overflow_size = overflow_size
    
    def execute(self) -> AttackResult:
        """
        Execute the ROP attack.
        
        Returns:
            Result of the attack
        """
        try:
            # Find the segment containing the stack
            segment = self.memory.find_segment(self.stack_address)
            if segment is None:
                return AttackResult(
                    success=False,
                    attack_type=AttackType.ROP,
                    error=f"Stack address 0x{self.stack_address:08x} not in any memory segment"
                )
            
            # Create the ROP chain
            payload = bytearray([0x41] * self.overflow_size)  # Initial buffer fill
            
            # Append gadget addresses
            for gadget_addr, _ in self.gadgets:
                payload.extend(gadget_addr.to_bytes(4, byteorder='little'))
            
            # Perform the buffer overflow with ROP chain
            result = self.vulnerability_injector.inject_buffer_overflow(
                self.stack_address,
                len(payload),
                payload
            )
            
            if not result["success"]:
                return AttackResult(
                    success=False,
                    attack_type=AttackType.ROP,
                    error=result["error"]
                )
            
            return AttackResult(
                success=True,
                attack_type=AttackType.ROP,
                details={
                    "stack_address": self.stack_address,
                    "overflow_size": self.overflow_size,
                    "gadget_count": len(self.gadgets),
                    "gadgets": [{"address": addr, "description": desc} for addr, desc in self.gadgets],
                    "payload_size": len(payload)
                }
            )
        except Exception as e:
            return AttackResult(
                success=False,
                attack_type=AttackType.ROP,
                error=str(e)
            )


class FormatStringAttack(Attack):
    """Format string attack implementation."""
    
    def __init__(
        self,
        memory: MemorySystem,
        format_address: int,
        target_address: Optional[int] = None,
        target_value: Optional[int] = None,
    ):
        """
        Initialize a format string attack.
        
        Args:
            memory: Memory system to attack
            format_address: Address where to place the format string
            target_address: Optional address to write to (for %n exploits)
            target_value: Optional value to write to target
        """
        super().__init__(memory)
        self.format_address = format_address
        self.target_address = target_address
        self.target_value = target_value
    
    def execute(self) -> AttackResult:
        """
        Execute the format string attack.
        
        Returns:
            Result of the attack
        """
        try:
            # Find the segment containing the format string
            segment = self.memory.find_segment(self.format_address)
            if segment is None:
                return AttackResult(
                    success=False,
                    attack_type=AttackType.FORMAT_STRING,
                    error=f"Format address 0x{self.format_address:08x} not in any memory segment"
                )
            
            # Create the format string payload
            if self.target_address is not None and self.target_value is not None:
                # Create a format string that will write target_value to target_address
                # This is a simplified example - real exploitation would be more complex
                
                # First, place the target address in the format string
                payload = self.target_address.to_bytes(4, byteorder='little')
                
                # Then create a format string that will write target_value bytes using %n
                # We need to output target_value characters before %n
                if self.target_value <= 8:
                    # Simple case for small values
                    payload += f"{'A' * self.target_value}%n".encode('utf-8')
                else:
                    # For larger values, use width specifier
                    payload += f"%{self.target_value}x%n".encode('utf-8')
            else:
                # Simple info leak format string
                payload = b"%x %x %x %x %x %x %x %x %x %x"
            
            # Inject the format string
            result = self.vulnerability_injector.inject_format_string(
                self.format_address,
                payload
            )
            
            if not result["success"]:
                return AttackResult(
                    success=False,
                    attack_type=AttackType.FORMAT_STRING,
                    error=result["error"]
                )
            
            # Verify target was overwritten if applicable
            if self.target_address is not None and self.target_value is not None:
                try:
                    actual_value = self.memory.read_word(self.target_address, {"operation": "verify_attack"})
                    
                    return AttackResult(
                        success=actual_value == self.target_value,
                        attack_type=AttackType.FORMAT_STRING,
                        details={
                            "format_address": self.format_address,
                            "target_address": self.target_address,
                            "target_value": self.target_value,
                            "actual_value": actual_value,
                            "payload_size": len(payload)
                        }
                    )
                except:
                    # Can't verify target value, but attack was executed
                    return AttackResult(
                        success=True,
                        attack_type=AttackType.FORMAT_STRING,
                        details={
                            "format_address": self.format_address,
                            "target_address": self.target_address,
                            "target_value": self.target_value,
                            "verification": "failed",
                            "payload_size": len(payload)
                        }
                    )
            
            # No verification needed
            return AttackResult(
                success=True,
                attack_type=AttackType.FORMAT_STRING,
                details={
                    "format_address": self.format_address,
                    "payload": payload.decode('utf-8', errors='ignore'),
                    "payload_size": len(payload)
                }
            )
        except Exception as e:
            return AttackResult(
                success=False,
                attack_type=AttackType.FORMAT_STRING,
                error=str(e)
            )


class ControlFlowHijackAttack(Attack):
    """Control flow hijack attack implementation."""
    
    def __init__(
        self,
        memory: MemorySystem,
        return_address: int,
        target_address: int,
        overflow_address: Optional[int] = None,
        overflow_size: Optional[int] = None,
    ):
        """
        Initialize a control flow hijack attack.
        
        Args:
            memory: Memory system to attack
            return_address: Address of the return address to overwrite
            target_address: Address to redirect execution to
            overflow_address: Optional address for buffer overflow
            overflow_size: Optional size for buffer overflow
        """
        super().__init__(memory)
        self.return_address = return_address
        self.target_address = target_address
        self.overflow_address = overflow_address
        self.overflow_size = overflow_size
    
    def execute(self) -> AttackResult:
        """
        Execute the control flow hijack attack.
        
        Returns:
            Result of the attack
        """
        try:
            # Find the segment containing the return address
            segment = self.memory.find_segment(self.return_address)
            if segment is None:
                return AttackResult(
                    success=False,
                    attack_type=AttackType.CONTROL_FLOW_HIJACK,
                    error=f"Return address 0x{self.return_address:08x} not in any memory segment"
                )
            
            if self.overflow_address is not None and self.overflow_size is not None:
                # Use buffer overflow to hijack control flow
                
                # Calculate offset from overflow to return address
                offset = self.return_address - self.overflow_address
                
                if offset < 0 or offset > self.overflow_size:
                    return AttackResult(
                        success=False,
                        attack_type=AttackType.CONTROL_FLOW_HIJACK,
                        error=f"Return address out of range for overflow (offset: {offset})"
                    )
                
                # Create payload
                payload = bytearray([0x41] * offset)  # Padding
                payload.extend(self.target_address.to_bytes(4, byteorder='little'))  # Target address
                
                # Fill any remaining buffer
                if len(payload) < self.overflow_size:
                    payload.extend([0x42] * (self.overflow_size - len(payload)))
                
                # Perform the buffer overflow
                result = self.vulnerability_injector.inject_buffer_overflow(
                    self.overflow_address,
                    len(payload),
                    payload
                )
            else:
                # Direct overwrite of return address
                try:
                    # Write the target address directly to the return address
                    self.memory.write_word(
                        self.return_address,
                        self.target_address,
                        {"attack": "control_flow_hijack"}
                    )
                    
                    result = {"success": True}
                except Exception as e:
                    result = {"success": False, "error": str(e)}
            
            if not result["success"]:
                return AttackResult(
                    success=False,
                    attack_type=AttackType.CONTROL_FLOW_HIJACK,
                    error=result.get("error", "Unknown error")
                )
            
            # Verify return address was overwritten
            try:
                actual_value = self.memory.read_word(self.return_address, {"operation": "verify_attack"})
                
                return AttackResult(
                    success=actual_value == self.target_address,
                    attack_type=AttackType.CONTROL_FLOW_HIJACK,
                    details={
                        "return_address": self.return_address,
                        "target_address": self.target_address,
                        "actual_value": actual_value,
                        "overflow_used": self.overflow_address is not None,
                        "overflow_address": self.overflow_address,
                        "overflow_size": self.overflow_size
                    }
                )
            except:
                # Can't verify return address, but attack was executed
                return AttackResult(
                    success=True,
                    attack_type=AttackType.CONTROL_FLOW_HIJACK,
                    details={
                        "return_address": self.return_address,
                        "target_address": self.target_address,
                        "verification": "failed",
                        "overflow_used": self.overflow_address is not None,
                        "overflow_address": self.overflow_address,
                        "overflow_size": self.overflow_size
                    }
                )
        except Exception as e:
            return AttackResult(
                success=False,
                attack_type=AttackType.CONTROL_FLOW_HIJACK,
                error=str(e)
            )