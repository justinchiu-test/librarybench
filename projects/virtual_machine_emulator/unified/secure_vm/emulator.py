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

from common.core.vm import VirtualMachine as BaseVirtualMachine, ExecutionEvent, Thread
from common.core.memory import MemorySystem, MemoryAccessType, MemoryPermission
from common.core.processor import Processor, ProcessorState, PrivilegeLevel
from common.core.instruction import Instruction, InstructionType
from common.core.exceptions import (
    VMException, MemoryException, ProcessorException, ExecutionLimitException
)

from secure_vm.memory import (
    Memory, MemorySegment, MemoryPermission, MemoryProtectionLevel, MemoryProtection
)
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


class ForensicLog:
    """Forensic logging system for the VM."""
    
    def __init__(self, enabled: bool = True, detailed: bool = False):
        self.enabled = enabled
        self.detailed = detailed
        self.logs: List[Dict[str, Any]] = []
        self.start_time = time.time()
    
    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log an event if logging is enabled."""
        if not self.enabled:
            return
        
        entry = {
            "timestamp": time.time() - self.start_time,
            "event_type": event_type,
            "data": data,
        }
        self.logs.append(entry)
    
    def log_memory_access(
        self,
        address: int,
        access_type: str,
        size: int,
        value: Optional[int] = None,
        context: Dict[str, Any] = None,
    ) -> None:
        """Log a memory access event."""
        if not self.enabled or not self.detailed:
            return
        
        data = {
            "address": address,
            "access_type": access_type,
            "size": size,
        }
        if value is not None:
            data["value"] = value
        if context:
            data["context"] = context
        
        self.log_event("memory_access", data)
    
    def log_control_flow(self, event: Dict[str, Any]) -> None:
        """Log a control flow event."""
        if not self.enabled:
            return
        
        self.log_event("control_flow", event)
    
    def log_protection_violation(self, event: Dict[str, Any]) -> None:
        """Log a protection violation event."""
        if not self.enabled:
            return
        
        self.log_event("protection_violation", event)
    
    def log_system_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """Log a system-level event."""
        if not self.enabled:
            return
        
        data = {"system_event": event_type, **details}
        self.log_event("system", data)
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """Get all logged events."""
        return self.logs
    
    def export_logs(self, format_type: str = "dict") -> Union[List[Dict[str, Any]], str]:
        """Export logs in the specified format."""
        if format_type == "dict":
            return self.logs
        elif format_type == "json":
            import json
            return json.dumps(self.logs, indent=2)
        elif format_type == "text":
            text_logs = []
            for log in self.logs:
                timestamp = log["timestamp"]
                event_type = log["event_type"]
                data_str = ", ".join(f"{k}={v}" for k, v in log["data"].items())
                text_logs.append(f"[{timestamp:.6f}] {event_type}: {data_str}")
            return "\n".join(text_logs)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")


class VirtualMachine(BaseVirtualMachine):
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
            num_processors=1,  # Secure VM uses a single CPU
            memory_size=memory_size,
            random_seed=random_seed,
            enable_tracing=True  # Always enable tracing for security monitoring
        )
        
        # Default memory protection if none provided
        if protection is None:
            protection = MemoryProtection(
                level=MemoryProtectionLevel.STANDARD,
                dep_enabled=True,
                aslr_enabled=False,
                stack_canaries=False,
                shadow_memory=False,
            )
        
        # Store protection settings
        self.protection = protection
        
        # Initialize forensic logging
        self.forensic_log = ForensicLog(
            enabled=enable_forensics,
            detailed=detailed_logging,
        )
        
        # Track loaded programs
        self.program_loaded = False
        self.program_name = ""
        self.program_entry_point = 0
        
        # Set up memory layout 
        self._setup_memory_layout(memory_size)
        
        # Apply memory protections
        self._apply_memory_protections()
    
    def _create_memory_system(self, memory_size: int) -> MemorySystem:
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
    
    def _create_processors(self, num_processors: int) -> List[Processor]:
        """
        Create the processors for this VM.
        
        Args:
            num_processors: Number of processors to create
            
        Returns:
            List of processor instances
        """
        # Secure VM uses a single CPU
        return [CPU(self.memory)]
    
    def _setup_memory_layout(self, memory_size: int) -> None:
        """Set up the standard memory layout for the VM."""
        # Calculate segment sizes
        code_size = memory_size // 4
        data_size = memory_size // 4
        heap_size = memory_size // 4
        stack_size = memory_size - code_size - data_size - heap_size
        
        # Create memory segments
        self.code_segment = self.memory.add_segment(
            MemorySegment(
                base_address=0x10000,
                size=code_size,
                permission=MemoryPermission.READ_EXECUTE,
                name="code"
            )
        )
        
        self.data_segment = self.memory.add_segment(
            MemorySegment(
                base_address=0x20000,
                size=data_size,
                permission=MemoryPermission.READ_WRITE,
                name="data"
            )
        )
        
        self.heap_segment = self.memory.add_segment(
            MemorySegment(
                base_address=0x30000,
                size=heap_size,
                permission=MemoryPermission.READ_WRITE,
                name="heap"
            )
        )
        
        self.stack_segment = self.memory.add_segment(
            MemorySegment(
                base_address=0x70000,
                size=stack_size,
                permission=MemoryPermission.READ_WRITE,
                name="stack"
            )
        )
        
        # Initialize stack pointer to top of stack
        self.processors[0].registers.sp = self.stack_segment.base_address + self.stack_segment.size - 4
        self.processors[0].registers.bp = self.processors[0].registers.sp
    
    def _apply_memory_protections(self) -> None:
        """Apply configured memory protections."""
        self.protection.apply_to_memory(self.memory)
        
        # Apply segment-specific protections
        self.protection.apply_to_segment(self.stack_segment, self.memory)
        
        # Log the memory protection configuration
        self.forensic_log.log_system_event(
            "memory_protection_config",
            self.protection.get_protection_description()
        )
        
        # Log the memory map
        self.forensic_log.log_system_event(
            "memory_map",
            {"segments": self.memory.get_memory_map()}
        )
    
    @property
    def cpu(self) -> CPU:
        """Get the CPU for convenience (Secure VM only has one processor)."""
        return self.processors[0]
    
    def get_instruction(self, address: int) -> Optional[Instruction]:
        """
        Get the instruction at the given address.
        
        Args:
            address: The memory address
            
        Returns:
            The instruction at the address, or None if not found
        """
        try:
            # Get the opcode from memory
            opcode = self.memory.execute(address, {"instruction_fetch": True})
            
            # Decode the instruction using the CPU's decoder
            name, instr_type, operand_count, required_privilege = self.cpu.decode_instruction(opcode)
            
            # Create and return an instruction object
            return Instruction(
                opcode=name,
                type=instr_type,
                operands=[f"R{i}" for i in range(operand_count)],
                privileged=(required_privilege is not None and 
                            required_privilege.value > PrivilegeLevel.USER.value)
            )
        except Exception:
            return None
    
    def schedule_threads(self) -> None:
        """
        Schedule threads to processors. Security VM has a simple scheduler
        since it only has one processor.
        """
        # If the CPU is idle and we have ready threads, assign the first one
        if not self.processors[0].is_busy() and self.ready_queue:
            thread_id = self.ready_queue.pop(0)
            if thread_id in self.threads:
                thread = self.threads[thread_id]
                self.processors[0].assign_thread(thread_id, thread.pc)
                thread.state = ProcessorState.RUNNING
                thread.processor_id = 0
                
                # Record thread scheduling
                event = ExecutionEvent(
                    event_type="thread_scheduled",
                    timestamp=self.global_clock,
                    thread_id=thread_id,
                    processor_id=0
                )
                self.add_execution_trace(event)
    
    def handle_side_effects(
        self,
        processor: Processor,
        thread: Thread,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> None:
        """
        Handle side effects from instruction execution, with security monitoring.
        
        Args:
            processor: The processor that executed the instruction
            thread: The thread that executed the instruction
            instruction: The instruction that was executed
            side_effects: Side effects from instruction execution
        """
        # Handle privilege changes
        if "privilege_change" in side_effects:
            change = side_effects["privilege_change"]
            self.forensic_log.log_system_event(
                "privilege_change",
                {
                    "thread_id": thread.thread_id,
                    "previous_level": change["previous_level"],
                    "new_level": change["new_level"],
                }
            )
        
        # Handle syscalls
        if "syscall_executed" in side_effects:
            syscall = side_effects["syscall_executed"]
            self.forensic_log.log_system_event(
                "syscall",
                {
                    "thread_id": thread.thread_id,
                    "number": syscall["number"],
                    "result": syscall["result"],
                }
            )
        
        # Handle control flow events (call/ret)
        if "call" in side_effects:
            call = side_effects["call"]
            self.forensic_log.log_system_event(
                "call",
                {
                    "thread_id": thread.thread_id,
                    "target": call["target"],
                    "return_addr": call["return_addr"],
                }
            )
        
        if "ret" in side_effects:
            ret = side_effects["ret"]
            self.forensic_log.log_system_event(
                "ret",
                {
                    "thread_id": thread.thread_id,
                    "return_addr": ret["return_addr"],
                    "shadow_valid": ret["shadow_valid"],
                }
            )
        
        # Handle halting
        if "halt" in side_effects:
            self.forensic_log.log_system_event(
                "halt",
                {
                    "thread_id": thread.thread_id,
                    "instruction_pointer": processor.registers.get_ip(),
                }
            )
    
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
    
    def get_forensic_logs(self, format_type: str = "dict") -> Union[List[Dict[str, Any]], str]:
        """Get forensic logs in the specified format."""
        return self.forensic_log.export_logs(format_type)
    
    def reset(self) -> None:
        """Reset the VM state while preserving configuration."""
        # Reset base VM
        super().reset()
        
        # Recreate memory with the same settings
        self.memory = self._create_memory_system(self.memory.size)
        
        # Reset CPU with new memory
        self.processors = [CPU(self.memory)]
        
        # Reset program state
        self.program_loaded = False
        self.program_name = ""
        self.program_entry_point = 0
        
        # Set up memory layout again
        self._setup_memory_layout(self.memory.size)
        
        # Apply memory protections
        self._apply_memory_protections()
        
        # Log reset
        self.forensic_log.log_system_event("reset", {})
    
    def get_control_flow_visualization(self, format_type: str = "dict") -> Union[Dict[str, Any], str]:
        """
        Generate a visualization of the control flow.
        
        This is useful for understanding how attacks manipulate program flow.
        """
        # Extract control flow records
        records = self.cpu.control_flow_records
        
        # Build a graph representation
        nodes = set()
        edges = []
        
        for record in records:
            nodes.add(record.from_address)
            nodes.add(record.to_address)
            
            edge = {
                "source": record.from_address,
                "target": record.to_address,
                "type": record.event_type,
                "legitimate": record.legitimate,
                "instruction": record.instruction,
            }
            edges.append(edge)
        
        nodes_list = [{"address": addr} for addr in sorted(nodes)]
        
        visualization = {
            "nodes": nodes_list,
            "edges": edges,
        }
        
        if format_type == "dict":
            return visualization
        elif format_type == "json":
            import json
            return json.dumps(visualization, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def get_memory_access_pattern(self) -> Dict[str, Dict[int, int]]:
        """
        Analyze memory access patterns from the forensic logs.
        
        Useful for identifying suspicious memory behavior.
        """
        if not self.forensic_log.detailed:
            return {"error": "Detailed logging must be enabled for memory access patterns"}
        
        patterns = {
            "read": {},
            "write": {},
            "execute": {},
        }
        
        for log in self.forensic_log.logs:
            if log["event_type"] == "memory_access":
                access_type = log["data"]["access_type"]
                address = log["data"]["address"]
                
                if access_type in patterns:
                    patterns[access_type][address] = patterns[access_type].get(address, 0) + 1
        
        return patterns
    
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