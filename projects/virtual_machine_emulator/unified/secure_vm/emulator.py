"""
Virtual Machine emulator for security research.

This module implements the main virtual machine emulator that integrates
the memory, CPU, and security components.
"""

from __future__ import annotations
import random
import time
import uuid
from typing import Dict, List, Optional, Set, Tuple, Union, Any, BinaryIO, Callable

from common.extensions.security.secure_vm import SecureVirtualMachine
from common.extensions.security.forensic_logging import ForensicLogger
from common.extensions.security.memory_protection import MemoryProtection, MemoryProtectionLevel
from common.core.memory import MemoryPermission

from secure_vm.memory import Memory, MemorySegment
from secure_vm.cpu import CPU, ControlFlowRecord


class ExecutionResult:
    """Result of executing a program in the VM."""
    
    def __init__(
        self,
        success: bool,
        cycles: int,
        execution_time: float,
        cpu_state: Dict[str, Any],
        control_flow_events: List[Dict[str, Any]],
        protection_events: List[Dict[str, Any]],
    ):
        self.success = success
        self.cycles = cycles
        self.execution_time = execution_time
        self.cpu_state = cpu_state
        self.control_flow_events = control_flow_events
        self.protection_events = protection_events
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the execution result."""
        return {
            "success": self.success,
            "cycles": self.cycles,
            "execution_time": self.execution_time,
            "control_flow_events": len(self.control_flow_events),
            "protection_events": len(self.protection_events),
            "instructions_per_second": self.cycles / max(self.execution_time, 0.001),
        }


class VirtualMachine(SecureVirtualMachine):
    """Virtual machine emulator for security research."""
    
    def __init__(
        self,
        memory_size: int = 65536,
        protection: Optional[MemoryProtection] = None,
        enable_forensics: bool = True,
        detailed_logging: bool = False,
        random_seed: Optional[int] = None,
    ):
        # Initialize base VM with security-specific settings
        super().__init__(
            memory_size=memory_size,
            protection=protection,
            enable_forensics=enable_forensics,
            detailed_logging=detailed_logging,
            random_seed=random_seed
        )
        
        # Track loaded programs
        self.program_loaded = False
        self.program_name = ""
    
    def _create_memory_system(self, memory_size: int) -> Memory:
        """
        Create the memory system for this VM.
        
        Args:
            memory_size: Size of memory in words
            
        Returns:
            The memory system instance
        """
        # Initialize memory with protection settings
        return Memory(
            protection_level=self.protection.level if hasattr(self, 'protection') else MemoryProtectionLevel.STANDARD,
            enable_dep=self.protection.dep_enabled if hasattr(self, 'protection') else True,
            enable_aslr=self.protection.aslr_enabled if hasattr(self, 'protection') else False,
        )
    
    def _create_processors(self, num_processors: int) -> List[CPU]:
        """
        Create the processors for this VM.
        
        Args:
            num_processors: Number of processors to create
            
        Returns:
            List of processor instances
        """
        # Secure VM uses a single CPU
        return [CPU(self.memory)]
    
    @property
    def cpu(self) -> CPU:
        """Get the CPU for convenience (Secure VM only has one processor)."""
        return self.processors[0]
    
    def load_program(self, program: List[int], entry_point: Optional[int] = None) -> None:
        """Load a program (instruction bytes) into the code segment."""
        if len(program) > self.code_segment.size:
            raise ValueError(f"Program size {len(program)} exceeds code segment size {self.code_segment.size}")

        # Temporarily modify code segment permissions to allow writing
        original_permission = self.code_segment.permission
        self.code_segment.permission = MemoryPermission.READ_WRITE_EXECUTE

        # Write program bytes to code segment
        for i, byte in enumerate(program):
            self.memory.write_byte(
                self.code_segment.base_address + i,
                byte,
                {"operation": "program_load"}
            )

        # Restore original permissions
        self.code_segment.permission = original_permission

        # Set default entry point
        if entry_point is None:
            entry_point = self.code_segment.base_address

        self.program_entry_point = entry_point
        self.program_loaded = True

        # Set instruction pointer to entry point
        self.cpu.registers.ip = entry_point
        
        # Create a main thread at the entry point
        main_thread_id = self.create_thread(entry_point)
        
        # Log program load
        self.forensic_log.log_system_event(
            "program_load",
            {
                "size": len(program),
                "entry_point": entry_point,
                "main_thread_id": main_thread_id,
            }
        )
    
    def load_program_from_file(self, filename: str, entry_point: Optional[int] = None) -> None:
        """Load a program from a binary file."""
        with open(filename, "rb") as f:
            program = list(f.read())
        
        self.program_name = filename
        self.load_program(program, entry_point)
    
    def load_data(self, data: List[int], data_address: Optional[int] = None) -> int:
        """Load data into the data segment and return the address where it was loaded."""
        if data_address is None:
            data_address = self.data_segment.base_address
        
        if not self.data_segment.contains_address(data_address) or not self.data_segment.contains_address(data_address + len(data) - 1):
            raise ValueError(f"Data doesn't fit in data segment at address 0x{data_address:08x}")
        
        # Write data bytes
        for i, byte in enumerate(data):
            self.memory.write_byte(
                data_address + i,
                byte,
                {"operation": "data_load"}
            )
        
        # Log data load
        self.forensic_log.log_system_event(
            "data_load",
            {
                "address": data_address,
                "size": len(data),
            }
        )
        
        return data_address
    
    def run(self, max_instructions: int = 10000) -> ExecutionResult:
        """Run the loaded program for up to max_instructions."""
        if not self.program_loaded:
            raise RuntimeError("No program loaded")
        
        # Log execution start
        self.forensic_log.log_system_event(
            "execution_start",
            {
                "entry_point": self.cpu.registers.ip,
                "max_instructions": max_instructions,
            }
        )
        
        # Run the VM
        try:
            # Use the base VM's run method
            cycles_executed = super().run(max_instructions)
            success = True
        except Exception as e:
            cycles_executed = self.global_clock
            success = False
            # Log the exception
            self.forensic_log.log_system_event(
                "execution_exception",
                {
                    "exception_type": type(e).__name__,
                    "message": str(e),
                    "instruction_pointer": self.cpu.registers.ip,
                }
            )
        
        # Log execution end
        self.forensic_log.log_system_event(
            "execution_end",
            {
                "cycles": cycles_executed,
                "success": success,
                "halted": self.cpu.halted,
            }
        )
        
        # Process control flow records for forensic log
        control_flow_events = []
        for record in self.cpu.control_flow_records:
            event = {
                "from_address": record.from_address,
                "to_address": record.to_address,
                "event_type": record.event_type,
                "instruction": record.instruction,
                "legitimate": record.legitimate,
                "timestamp": record.timestamp,
            }
            if record.context:
                event["context"] = record.context
            
            control_flow_events.append(event)
            self.forensic_log.log_control_flow(event)
        
        # Process protection events
        protection_events = []
        for event in self.memory.protection_events:
            protection_event = {
                "address": event.address,
                "access_type": event.access_type,
                "current_permission": event.current_permission.name,
                "required_permission": event.required_permission.name,
                "instruction_pointer": event.instruction_pointer,
            }
            if event.context:
                protection_event["context"] = event.context
            
            protection_events.append(protection_event)
            self.forensic_log.log_protection_violation(protection_event)
        
        # Create execution result
        result = ExecutionResult(
            success=success,
            cycles=cycles_executed,
            execution_time=self.end_time - self.start_time if self.end_time > 0 else 0,
            cpu_state=self.cpu.registers.dump_registers(),
            control_flow_events=control_flow_events,
            protection_events=protection_events,
        )
        
        return result
    
    def inject_vulnerability(
        self,
        vuln_type: str,
        address: int,
        size: int,
        payload: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """
        Inject a vulnerability into memory for demonstration purposes.
        
        This is useful for creating controlled security vulnerabilities
        that can be exploited through different attack vectors.
        """
        self.forensic_log.log_system_event(
            "vulnerability_injection",
            {
                "type": vuln_type,
                "address": address,
                "size": size,
                "has_payload": payload is not None,
            }
        )
        
        result = {"success": False, "error": None}
        
        try:
            if vuln_type == "buffer_overflow":
                # Create a buffer overflow condition
                segment = self.memory.find_segment(address)
                if segment is None:
                    result["error"] = f"Address 0x{address:08x} not in any memory segment"
                    return result
                
                # Write beyond intended buffer size
                data = payload or bytes([0x41] * size)  # Default to 'A's if no payload
                self.memory.write_bytes(address, data, {"vulnerability": "buffer_overflow"})
                result["success"] = True
                
            elif vuln_type == "use_after_free":
                # Simulate a use-after-free by marking memory as "freed" but still accessible
                segment = self.memory.find_segment(address)
                if segment is None:
                    result["error"] = f"Address 0x{address:08x} not in any memory segment"
                    return result
                
                # In a real scenario, we'd actually free this memory, but for demonstration,
                # we'll just modify it to show it was "freed" but still accessible
                data = payload or bytes([0xDD] * size)  # Default to a "freed memory" pattern
                self.memory.write_bytes(address, data, {"vulnerability": "use_after_free"})
                result["success"] = True
                
            elif vuln_type == "format_string":
                # Simulate a format string vulnerability
                segment = self.memory.find_segment(address)
                if segment is None:
                    result["error"] = f"Address 0x{address:08x} not in any memory segment"
                    return result
                
                # Create a "format string" in memory
                format_string = payload or b"%x%x%x%n"
                self.memory.write_bytes(address, format_string, {"vulnerability": "format_string"})
                result["success"] = True
                
            elif vuln_type == "code_injection":
                # Inject executable code into a writeable memory segment
                segment = self.memory.find_segment(address)
                if segment is None:
                    result["error"] = f"Address 0x{address:08x} not in any memory segment"
                    return result
                
                # This would normally be caught by DEP, but we allow it for demonstration
                shellcode = payload or bytes([0x90] * (size - 2) + [0x90, 0xC3])  # NOP sled + RET
                self.memory.write_bytes(address, shellcode, {"vulnerability": "code_injection"})
                result["success"] = True
                
            else:
                result["error"] = f"Unknown vulnerability type: {vuln_type}"
        
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def get_memory_snapshot(self, segment_name: str = None) -> Dict[str, Any]:
        """Get a snapshot of memory contents, optionally filtered by segment name."""
        segments = []
        
        for segment in self.memory.segments:
            if segment_name is None or segment.name == segment_name:
                # Create a snapshot of this segment
                snapshot = {
                    "name": segment.name,
                    "base_address": segment.base_address,
                    "size": segment.size,
                    "permission": segment.permission.name,
                    "data": bytes(segment.data),  # Convert to bytes for easier handling
                }
                segments.append(snapshot)
        
        return {"segments": segments}
    
    def compare_protection_strategies(
        self,
        strategies: List[MemoryProtection],
        program: List[int],
        attack: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Compare different memory protection strategies against the same attack.
        
        This is useful for educational purposes to show how different protections
        affect exploitability.
        """
        results = []
        
        for strategy in strategies:
            # Reset VM and apply new protection strategy
            self.reset()
            self.protection = strategy
            self._apply_memory_protections()
            
            # Load the program
            self.load_program(program)
            
            # Set up the attack
            if attack["type"] == "buffer_overflow":
                self.inject_vulnerability(
                    "buffer_overflow",
                    attack["address"],
                    attack["size"],
                    attack.get("payload")
                )
            elif attack["type"] == "code_injection":
                self.inject_vulnerability(
                    "code_injection",
                    attack["address"],
                    attack["size"],
                    attack.get("payload")
                )
            # Add other attack types as needed
            
            # Run the program
            execution_result = self.run()
            
            # Collect results
            results.append({
                "protection": strategy.get_protection_description(),
                "attack_successful": not execution_result.success,
                "protection_events": len(execution_result.protection_events),
                "execution_result": execution_result.get_summary(),
            })
        
        return results