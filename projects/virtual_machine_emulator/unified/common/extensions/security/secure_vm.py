"""
Secure virtual machine extension.

This module provides a security-focused VM implementation that integrates
all security extensions, including memory protection, control flow integrity,
vulnerability detection, and forensic logging.
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

from common.extensions.security.memory_protection import (
    MemoryProtectionLevel, 
    MemoryProtection, 
    SecureMemorySystem, 
    SecureMemorySegment
)
from common.extensions.security.control_flow import (
    ControlFlowIntegrityMonitor,
    ControlFlowVisualization
)
from common.extensions.security.forensic_logging import ForensicLog, ForensicReport
from common.extensions.security.vulnerability_detection import VulnerabilityInjector


class ExecutionResult:
    """Result of executing a program in the secure VM."""
    
    def __init__(
        self,
        success: bool,
        cycles: int,
        execution_time: float,
        cpu_state: Dict[str, Any],
        control_flow_events: List[Dict[str, Any]],
        protection_events: List[Dict[str, Any]],
    ):
        """
        Initialize the execution result.
        
        Args:
            success: Whether execution completed successfully
            cycles: Number of CPU cycles executed
            execution_time: Execution time in seconds
            cpu_state: Final CPU state
            control_flow_events: Control flow events during execution
            protection_events: Protection events during execution
        """
        self.success = success
        self.cycles = cycles
        self.execution_time = execution_time
        self.cpu_state = cpu_state
        self.control_flow_events = control_flow_events
        self.protection_events = protection_events
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the execution result.
        
        Returns:
            Execution result summary
        """
        return {
            "success": self.success,
            "cycles": self.cycles,
            "execution_time": self.execution_time,
            "control_flow_events": len(self.control_flow_events),
            "protection_events": len(self.protection_events),
            "instructions_per_second": self.cycles / max(self.execution_time, 0.001),
        }


class SecureVirtualMachine(BaseVirtualMachine):
    """
    Security-focused virtual machine implementation.
    
    This VM extends the base VM with comprehensive security features,
    including memory protection, control flow integrity monitoring,
    vulnerability detection, and forensic logging.
    """
    
    def __init__(
        self,
        memory_size: int = 65536,
        protection: Optional[MemoryProtection] = None,
        enable_forensics: bool = True,
        detailed_logging: bool = False,
        random_seed: Optional[int] = None,
    ):
        """
        Initialize the secure virtual machine.
        
        Args:
            memory_size: Size of memory in bytes
            protection: Memory protection configuration
            enable_forensics: Whether to enable forensic logging
            detailed_logging: Whether to enable detailed logging
            random_seed: Random seed for reproducibility
        """
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
        
        # Initialize control flow integrity monitor
        self.cfi_monitor = ControlFlowIntegrityMonitor()
        
        # Initialize vulnerability injector
        if hasattr(self, 'memory'):
            self.vulnerability_injector = VulnerabilityInjector(self.memory)
        
        # Track loaded programs
        self.program_loaded = False
        self.program_name = ""
        self.program_entry_point = 0
        
        # Memory segments
        self.code_segment = None
        self.data_segment = None
        self.heap_segment = None
        self.stack_segment = None
        
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
        return SecureMemorySystem(
            size=memory_size,
            protection_level=self.protection.level if hasattr(self, 'protection') else MemoryProtectionLevel.STANDARD,
            enable_dep=self.protection.dep_enabled if hasattr(self, 'protection') else True,
            enable_aslr=self.protection.aslr_enabled if hasattr(self, 'protection') else False,
        )
    
    def _setup_memory_layout(self, memory_size: int) -> None:
        """
        Set up the standard memory layout for the VM.
        
        Args:
            memory_size: Size of memory in bytes
        """
        # Calculate segment sizes
        code_size = memory_size // 4
        data_size = memory_size // 4
        heap_size = memory_size // 4
        stack_size = memory_size - code_size - data_size - heap_size
        
        # Create memory segments
        self.code_segment = self.memory.add_segment(
            SecureMemorySegment(
                base_address=0x10000,
                size=code_size,
                permission=MemoryPermission.READ_EXECUTE,
                name="code"
            )
        )
        
        self.data_segment = self.memory.add_segment(
            SecureMemorySegment(
                base_address=0x20000,
                size=data_size,
                permission=MemoryPermission.READ_WRITE,
                name="data"
            )
        )
        
        self.heap_segment = self.memory.add_segment(
            SecureMemorySegment(
                base_address=0x30000,
                size=heap_size,
                permission=MemoryPermission.READ_WRITE,
                name="heap"
            )
        )
        
        self.stack_segment = self.memory.add_segment(
            SecureMemorySegment(
                base_address=0x70000,
                size=stack_size,
                permission=MemoryPermission.READ_WRITE,
                name="stack"
            )
        )
        
        # Initialize stack pointer to top of stack
        if hasattr(self, 'processors') and len(self.processors) > 0:
            if hasattr(self.processors[0], 'registers'):
                if hasattr(self.processors[0].registers, 'sp'):
                    self.processors[0].registers.sp = self.stack_segment.base_address + self.stack_segment.size - 4
                if hasattr(self.processors[0].registers, 'bp'):
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
        if hasattr(self.memory, 'get_memory_map'):
            self.forensic_log.log_system_event(
                "memory_map",
                {"segments": self.memory.get_memory_map()}
            )
    
    def record_control_flow_event(
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
            event_type: Type of event
            instruction: Instruction that caused the event
            legitimate: Whether the control flow is legitimate
            context: Additional context
        """
        record = self.cfi_monitor.record_control_flow(
            from_address, 
            to_address, 
            event_type, 
            instruction, 
            legitimate, 
            context
        )
        self.forensic_log.log_control_flow(record)
    
    def inject_vulnerability(
        self,
        vuln_type: str,
        address: int,
        size: int,
        payload: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """
        Inject a vulnerability into memory for testing and demonstration.
        
        Args:
            vuln_type: Type of vulnerability
            address: Target memory address
            size: Size in bytes
            payload: Optional payload
            
        Returns:
            Result of vulnerability injection
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
        
        if vuln_type == "buffer_overflow":
            return self.vulnerability_injector.inject_buffer_overflow(address, size, payload)
        elif vuln_type == "format_string":
            return self.vulnerability_injector.inject_format_string(address, size, payload)
        elif vuln_type == "code_injection":
            return self.vulnerability_injector.inject_code_execution(address, size, payload)
        elif vuln_type == "use_after_free":
            return self.vulnerability_injector.inject_use_after_free(address, size, payload)
        else:
            return {"success": False, "error": f"Unknown vulnerability type: {vuln_type}"}
    
    def load_program(self, program: List[int], entry_point: Optional[int] = None) -> None:
        """
        Load a program into memory.
        
        Args:
            program: Program bytes
            entry_point: Optional entry point address
        """
        if hasattr(self, 'code_segment') and self.code_segment is not None:
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
            if hasattr(self, 'processors') and len(self.processors) > 0:
                if hasattr(self.processors[0], 'registers'):
                    if hasattr(self.processors[0].registers, 'ip'):
                        self.processors[0].registers.ip = entry_point
            
            # Log program load
            self.forensic_log.log_system_event(
                "program_load",
                {
                    "size": len(program),
                    "entry_point": entry_point,
                }
            )
    
    def run(self, max_instructions: int = 10000) -> ExecutionResult:
        """
        Run the VM with enhanced security monitoring.
        
        Args:
            max_instructions: Maximum instructions to execute
            
        Returns:
            Execution result
        """
        if not self.program_loaded:
            raise RuntimeError("No program loaded")
        
        # Log execution start
        self.forensic_log.log_system_event(
            "execution_start",
            {
                "entry_point": self.processors[0].registers.ip if hasattr(self.processors[0], 'registers') else 0,
                "max_instructions": max_instructions,
            }
        )
        
        # Run the VM
        try:
            # Use the base VM's run method
            self.start_time = time.time()
            cycles_executed = super().run(max_instructions)
            self.end_time = time.time()
            success = True
        except Exception as e:
            self.end_time = time.time()
            cycles_executed = self.global_clock
            success = False
            # Log the exception
            self.forensic_log.log_system_event(
                "execution_exception",
                {
                    "exception_type": type(e).__name__,
                    "message": str(e),
                    "instruction_pointer": (
                        self.processors[0].registers.ip 
                        if hasattr(self.processors[0], 'registers') 
                        else 0
                    ),
                }
            )
        
        # Log execution end
        self.forensic_log.log_system_event(
            "execution_end",
            {
                "cycles": cycles_executed,
                "success": success,
                "halted": self.processors[0].halted if hasattr(self.processors[0], 'halted') else False,
            }
        )
        
        # Process control flow records
        control_flow_events = []
        for record in self.cfi_monitor.get_control_flow_records():
            event = record.to_dict()
            control_flow_events.append(event)
        
        # Process protection events
        protection_events = []
        if hasattr(self.memory, 'protection_events'):
            for event in self.memory.protection_events:
                if hasattr(event, 'to_dict'):
                    protection_event = event.to_dict()
                else:
                    # Fallback if to_dict is not available
                    protection_event = {
                        "address": event.address if hasattr(event, 'address') else 0,
                        "access_type": event.access_type if hasattr(event, 'access_type') else "unknown",
                        "current_permission": (
                            event.current_permission.name 
                            if hasattr(event, 'current_permission') and hasattr(event.current_permission, 'name')
                            else "unknown"
                        ),
                        "required_permission": (
                            event.required_permission.name
                            if hasattr(event, 'required_permission') and hasattr(event.required_permission, 'name')
                            else "unknown"
                        ),
                        "instruction_pointer": event.instruction_pointer if hasattr(event, 'instruction_pointer') else 0,
                    }
                    if hasattr(event, 'context'):
                        protection_event["context"] = event.context
                
                protection_events.append(protection_event)
                self.forensic_log.log_protection_violation(protection_event)
        
        # Create execution result
        result = ExecutionResult(
            success=success,
            cycles=cycles_executed,
            execution_time=self.end_time - self.start_time if self.end_time > 0 else 0,
            cpu_state=(
                self.processors[0].registers.dump_registers() 
                if hasattr(self.processors[0], 'registers') and hasattr(self.processors[0].registers, 'dump_registers')
                else {}
            ),
            control_flow_events=control_flow_events,
            protection_events=protection_events,
        )
        
        return result
    
    def get_forensic_logs(self, format_type: str = "dict") -> Union[List[Dict[str, Any]], str]:
        """
        Get forensic logs in the specified format.
        
        Args:
            format_type: Format to export logs in (dict, json, text)
            
        Returns:
            Forensic logs in the requested format
        """
        return self.forensic_log.export_logs(format_type)
    
    def get_control_flow_visualization(self, format_type: str = "dict") -> Union[Dict[str, Any], str]:
        """
        Generate a visualization of control flow events.
        
        Args:
            format_type: Format to generate (dict, json)
            
        Returns:
            Control flow visualization in the requested format
        """
        # Create visualization
        visualization = ControlFlowVisualization(self.cfi_monitor.get_control_flow_records())
        graph = visualization.generate_graph()
        
        if format_type == "dict":
            return graph
        elif format_type == "json":
            import json
            return json.dumps(graph, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def get_security_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive security report.
        
        Returns:
            Security report
        """
        report = ForensicReport(self.forensic_log)
        
        # Build the report
        return {
            "summary": report.generate_summary(),
            "memory_access_pattern": report.get_memory_access_pattern(),
            "control_flow": report.get_control_flow_graph(),
            "protection_level": self.protection.get_protection_description(),
            "segments": [
                {"name": self.code_segment.name, "base": self.code_segment.base_address, "size": self.code_segment.size, "permission": self.code_segment.permission.name},
                {"name": self.data_segment.name, "base": self.data_segment.base_address, "size": self.data_segment.size, "permission": self.data_segment.permission.name},
                {"name": self.heap_segment.name, "base": self.heap_segment.base_address, "size": self.heap_segment.size, "permission": self.heap_segment.permission.name},
                {"name": self.stack_segment.name, "base": self.stack_segment.base_address, "size": self.stack_segment.size, "permission": self.stack_segment.permission.name},
            ],
            "control_flow_violations": visualization.highlight_violations(),
        }
    
    def reset(self) -> None:
        """Reset the VM state while preserving configuration."""
        # Reset base VM
        super().reset()
        
        # Reset security-specific components
        self.cfi_monitor.reset()
        self.forensic_log.clear_logs()
        
        # Recreate memory with the same settings
        self.memory = self._create_memory_system(
            getattr(self.memory, 'size', 65536)
        )
        
        # Reset processors 
        self.processors = [self._create_processors(1)[0]]
        
        # Reset program state
        self.program_loaded = False
        self.program_name = ""
        self.program_entry_point = 0
        
        # Set up memory layout again
        self._setup_memory_layout(getattr(self.memory, 'size', 65536))
        
        # Apply memory protections
        self._apply_memory_protections()
        
        # Recreate vulnerability injector
        self.vulnerability_injector = VulnerabilityInjector(self.memory)
        
        # Log reset
        self.forensic_log.log_system_event("reset", {})