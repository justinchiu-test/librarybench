"""
Secure Virtual Machine for security research.

This module integrates the various security extensions to provide a
comprehensive secure VM implementation:
- Memory protection features
- Control flow integrity monitoring
- Vulnerability detection and injection
- Privilege level management
- Forensic logging and analysis
"""

import time
from typing import Dict, List, Optional, Set, Tuple, Union, Any, Callable, BinaryIO

from common.core.vm import VirtualMachine as BaseVirtualMachine
from common.core.memory import MemorySystem, MemorySegment, MemoryPermission
from common.core.processor import Processor, PrivilegeLevel
from common.core.instruction import Instruction, InstructionType
from common.core.exceptions import VMException, MemoryException, ProcessorException

from common.extensions.security.memory_protection import (
    MemoryProtection, MemoryProtectionLevel, MemoryProtectionException
)
from common.extensions.security.control_flow import (
    ControlFlowMonitor, ControlFlowException, ShadowStack
)
from common.extensions.security.forensic_logging import (
    ForensicLog, LoggingLevel, EventCategory, ForensicAnalyzer
)
from common.extensions.security.vulnerability_detection import (
    VulnerabilityDetector, VulnerabilityInjector, VulnerabilityType
)
from common.extensions.security.privilege import (
    PrivilegeManager, ProtectionKeyManager, SecureModeManager, SecureMode
)


class SecureExecutionResult:
    """Result of executing a program in the secure VM."""
    
    def __init__(
        self,
        success: bool,
        cycles: int,
        execution_time: float,
        processor_state: Dict[str, Any],
        security_events: Dict[str, List[Dict[str, Any]]],
    ):
        """
        Initialize the execution result.
        
        Args:
            success: Whether execution was successful
            cycles: Number of cycles executed
            execution_time: Total execution time
            processor_state: Processor state at completion
            security_events: Security-related events
        """
        self.success = success
        self.cycles = cycles
        self.execution_time = execution_time
        self.processor_state = processor_state
        self.security_events = security_events
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the execution result.
        
        Returns:
            Summary dictionary
        """
        # Count events by category
        event_counts = {}
        for category, events in self.security_events.items():
            event_counts[category] = len(events)
        
        return {
            "success": self.success,
            "cycles": self.cycles,
            "execution_time": self.execution_time,
            "instructions_per_second": self.cycles / max(self.execution_time, 0.001),
            "security_events": event_counts,
        }


class SecureVirtualMachine(BaseVirtualMachine):
    """
    Secure virtual machine for security research.
    
    This class integrates various security extensions to provide a
    comprehensive platform for security research and education.
    """
    
    def __init__(
        self,
        memory_size: int = 65536,
        memory_protection_level: MemoryProtectionLevel = MemoryProtectionLevel.STANDARD,
        enable_dep: bool = True,
        enable_aslr: bool = False,
        enable_stack_canaries: bool = False,
        enable_shadow_memory: bool = False,
        enable_control_flow_integrity: bool = True,
        logging_level: LoggingLevel = LoggingLevel.STANDARD,
        initial_secure_mode: SecureMode = SecureMode.PROTECTED,
        initial_privilege_level: PrivilegeLevel = PrivilegeLevel.USER,
        random_seed: Optional[int] = None,
    ):
        """
        Initialize the secure virtual machine.
        
        Args:
            memory_size: Size of memory in bytes
            memory_protection_level: Memory protection level
            enable_dep: Whether to enable DEP
            enable_aslr: Whether to enable ASLR
            enable_stack_canaries: Whether to enable stack canaries
            enable_shadow_memory: Whether to enable shadow memory
            enable_control_flow_integrity: Whether to enable CFI
            logging_level: Logging detail level
            initial_secure_mode: Initial secure execution mode
            initial_privilege_level: Initial privilege level
            random_seed: Random seed for deterministic execution
        """
        # Initialize base VM
        super().__init__(
            num_processors=1,  # Security VM is single-core
            memory_size=memory_size,
            random_seed=random_seed,
            enable_tracing=True,  # Always enable tracing for security analysis
        )
        
        # Configure memory protection
        self.memory_protection = MemoryProtection(
            level=memory_protection_level,
            dep_enabled=enable_dep,
            aslr_enabled=enable_aslr,
            stack_canaries=enable_stack_canaries,
            shadow_memory=enable_shadow_memory,
        )
        
        # Initialize security components
        self.control_flow_monitor = ControlFlowMonitor(enable_control_flow_integrity)
        self.forensic_log = ForensicLog(enabled=True, level=logging_level)
        self.forensic_analyzer = ForensicAnalyzer(self.forensic_log)
        self.vulnerability_detector = VulnerabilityDetector(self.memory)
        self.vulnerability_injector = VulnerabilityInjector(self.memory)
        self.privilege_manager = PrivilegeManager(initial_privilege_level)
        self.protection_key_manager = ProtectionKeyManager()
        self.secure_mode_manager = SecureModeManager(self.memory, initial_secure_mode)
        
        # Set up memory segments
        self._setup_memory_layout(memory_size)
        
        # Apply memory protections
        self._apply_memory_protections()
        
        # Initialize processor with security features
        self._configure_processor_security()
        
        # Program state
        self.program_loaded = False
        self.program_entry_point = 0
    
    def _create_memory_system(self, memory_size: int) -> MemorySystem:
        """
        Create the memory system for this VM.
        
        Args:
            memory_size: Size of memory in words
            
        Returns:
            The memory system instance
        """
        # Create a secure memory system - this will typically be
        # provided by the implementation using this extension
        from secure_vm.memory import Memory
        
        return Memory(
            protection_level=self.memory_protection.level if hasattr(self, 'memory_protection') else MemoryProtectionLevel.STANDARD,
            enable_dep=self.memory_protection.dep_enabled if hasattr(self, 'memory_protection') else True,
            enable_aslr=self.memory_protection.aslr_enabled if hasattr(self, 'memory_protection') else False,
        )
    
    def _create_processors(self, num_processors: int) -> List[Processor]:
        """
        Create the processors for this VM.
        
        Args:
            num_processors: Number of processors to create
            
        Returns:
            List of processor instances
        """
        # Create a secure processor - this will typically be
        # provided by the implementation using this extension
        from secure_vm.cpu import CPU
        
        return [CPU(self.memory)]
    
    def _setup_memory_layout(self, memory_size: int) -> None:
        """
        Set up the standard memory layout for the VM.
        
        Args:
            memory_size: Total memory size
        """
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
        
        # Log memory layout
        self.forensic_log.log_system_event(
            "memory_layout_initialized",
            {
                "segments": [
                    {
                        "name": segment.name,
                        "base_address": segment.base_address,
                        "size": segment.size,
                        "permission": segment.permission.name,
                    }
                    for segment in self.memory.segments
                ]
            }
        )
    
    def _apply_memory_protections(self) -> None:
        """Apply memory protection configuration."""
        # Apply global memory protections
        self.memory_protection.apply_to_memory(self.memory)
        
        # Apply segment-specific protections
        for segment in self.memory.segments:
            self.memory_protection.apply_to_segment(segment, self.memory)
            
            # Register segment with vulnerability detector
            if hasattr(segment, 'size'):
                self.vulnerability_detector.register_buffer(segment.base_address, segment.size)
        
        # Log the memory protection configuration
        self.forensic_log.log_system_event(
            "memory_protection_config",
            self.memory_protection.get_protection_description()
        )
    
    def _configure_processor_security(self) -> None:
        """Configure processor security features."""
        # This is typically for processor-specific security features
        pass
    
    def register_memory_access(
        self,
        address: int,
        access_type: str,
        size: int,
        value: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a memory access for security monitoring.
        
        Args:
            address: Memory address
            access_type: Type of access (read, write, execute)
            size: Size of access in bytes
            value: Optional value for write operations
            context: Additional context information
        """
        # Log the memory access
        self.forensic_log.log_memory_access(
            address, access_type, size, value, context
        )
        
        # Register access with vulnerability detector
        self.vulnerability_detector.register_memory_access(
            address, 
            access_type, 
            size, 
            self.processors[0].registers.get_pc(),
            context
        )
    
    def load_program(self, program: List[int], entry_point: Optional[int] = None) -> None:
        """
        Load a program into the code segment.
        
        Args:
            program: Program bytes
            entry_point: Optional entry point (defaults to code segment base)
        """
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
        if hasattr(self.processors[0].registers, 'ip'):
            self.processors[0].registers.ip = entry_point
        else:
            self.processors[0].registers.set_pc(entry_point)
        
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
        """
        Load a program from a binary file.
        
        Args:
            filename: Path to binary file
            entry_point: Optional entry point
        """
        with open(filename, "rb") as f:
            program = list(f.read())
        
        self.load_program(program, entry_point)
    
    def run(self, max_cycles: int = 10000) -> SecureExecutionResult:
        """
        Run the VM with security monitoring.
        
        Args:
            max_cycles: Maximum cycles to execute
            
        Returns:
            SecureExecutionResult with execution details
        """
        if not self.program_loaded:
            raise RuntimeError("No program loaded")
        
        # Log execution start
        self.forensic_log.log_system_event(
            "execution_start",
            {
                "entry_point": self.processors[0].registers.get_pc(),
                "max_cycles": max_cycles,
                "secure_mode": self.secure_mode_manager.current_mode.name,
                "privilege_level": self.privilege_manager.current_level.name,
            }
        )
        
        # Run the VM
        try:
            start_time = time.time()
            cycles_executed = super().run(max_cycles)
            execution_time = time.time() - start_time
            success = True
        except Exception as e:
            cycles_executed = self.global_clock
            execution_time = time.time() - start_time if hasattr(self, 'start_time') else 0
            success = False
            
            # Log the exception
            self.forensic_log.log_system_event(
                "execution_exception",
                {
                    "exception_type": type(e).__name__,
                    "message": str(e),
                    "instruction_pointer": self.processors[0].registers.get_pc(),
                }
            )
        
        # Log execution end
        self.forensic_log.log_system_event(
            "execution_end",
            {
                "cycles": cycles_executed,
                "success": success,
                "execution_time": execution_time,
            }
        )
        
        # Check for security issues
        security_report = self._generate_security_report()
        
        # Create execution result
        result = SecureExecutionResult(
            success=success,
            cycles=cycles_executed,
            execution_time=execution_time,
            processor_state=self.processors[0].registers.dump_registers(),
            security_events=security_report,
        )
        
        return result
    
    def _generate_security_report(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate a security report from the execution.
        
        Returns:
            Security report dictionary
        """
        # Collect security events
        security_events = {}
        
        # Control flow violations
        if hasattr(self, 'control_flow_monitor'):
            control_flow_anomalies = self.forensic_analyzer.detect_control_flow_anomalies()
            if control_flow_anomalies:
                security_events["control_flow_violations"] = control_flow_anomalies
        
        # Memory protection violations
        if hasattr(self, 'forensic_analyzer'):
            memory_violations = self.forensic_analyzer.detect_memory_protection_violations()
            if memory_violations:
                security_events["memory_violations"] = memory_violations
        
        # Privilege escalation
        if hasattr(self, 'forensic_analyzer'):
            privilege_escalations = self.forensic_analyzer.detect_privilege_escalation()
            if privilege_escalations:
                security_events["privilege_escalations"] = privilege_escalations
        
        # Detected vulnerabilities
        if hasattr(self, 'vulnerability_detector'):
            vulnerabilities = self.vulnerability_detector.detect_vulnerabilities()
            for vuln_type, vulns in vulnerabilities.items():
                if vulns:
                    security_events[f"{vuln_type.lower()}_vulnerabilities"] = vulns
        
        return security_events
    
    def inject_vulnerability(
        self,
        vuln_type: str,
        address: int,
        size: int,
        payload: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """
        Inject a vulnerability for security testing.
        
        Args:
            vuln_type: Type of vulnerability
            address: Target address
            size: Size parameter
            payload: Optional payload data
            
        Returns:
            Result of injection operation
        """
        # Convert string to enum
        try:
            vulnerability_type = getattr(VulnerabilityType, vuln_type.upper())
        except AttributeError:
            return {
                "success": False,
                "error": f"Unknown vulnerability type: {vuln_type}"
            }
        
        # Log the vulnerability injection
        self.forensic_log.log_system_event(
            "vulnerability_injection",
            {
                "type": vuln_type,
                "address": address,
                "size": size,
                "has_payload": payload is not None,
            }
        )
        
        # Inject the vulnerability
        return self.vulnerability_injector.inject_vulnerability(
            vulnerability_type,
            address,
            size,
            payload
        )
    
    def get_security_report(self) -> Dict[str, Any]:
        """
        Get a comprehensive security report.
        
        Returns:
            Security report dictionary
        """
        # Get forensic analyzer report
        forensic_report = self.forensic_analyzer.generate_security_report()
        
        # Add VM-specific information
        report = {
            "vm_state": {
                "privilege_level": self.privilege_manager.current_level.name,
                "secure_mode": self.secure_mode_manager.current_mode.name,
                "enabled_features": self.secure_mode_manager.get_current_features(),
                "memory_protection": self.memory_protection.get_protection_description(),
            },
            "forensic_analysis": forensic_report,
            "generated_at": time.time(),
        }
        
        return report
    
    def get_memory_snapshot(self, segment_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a snapshot of memory contents.
        
        Args:
            segment_name: Optional segment name filter
            
        Returns:
            Memory snapshot dictionary
        """
        segments = []
        
        for segment in self.memory.segments:
            if segment_name is None or segment.name == segment_name:
                # Create a snapshot of this segment
                snapshot = {
                    "name": segment.name,
                    "base_address": segment.base_address,
                    "size": segment.size,
                    "permission": segment.permission.name,
                }
                
                # Include data if not too large
                if hasattr(segment, 'data') and len(segment.data) <= 1024:
                    snapshot["data"] = bytes(segment.data).hex()
                
                segments.append(snapshot)
        
        return {"segments": segments}
    
    def get_forensic_logs(self, format_type: str = "dict") -> Union[List[Dict[str, Any]], str]:
        """
        Get forensic logs in specified format.
        
        Args:
            format_type: Output format (dict, json, or text)
            
        Returns:
            Forensic logs in requested format
        """
        return self.forensic_log.export_logs(format_type)
    
    def analyze_control_flow(self) -> Dict[str, Any]:
        """
        Analyze control flow integrity.
        
        Returns:
            Control flow analysis
        """
        # Get control flow statistics
        if hasattr(self.control_flow_monitor, 'get_statistics'):
            stats = self.control_flow_monitor.get_statistics()
        else:
            stats = {"error": "Control flow monitor not initialized"}
        
        # Get visualization
        if hasattr(self.control_flow_monitor, 'get_control_flow_visualization'):
            viz = self.control_flow_monitor.get_control_flow_visualization("dict")
        else:
            viz = {"error": "Control flow visualization not available"}
        
        return {
            "statistics": stats,
            "visualization": viz,
            "anomalies": self.forensic_analyzer.detect_control_flow_anomalies()
        }
    
    def reset(self) -> None:
        """Reset the VM to initial state."""
        # Reset base VM
        super().reset()
        
        # Reset security components
        if hasattr(self, 'control_flow_monitor'):
            self.control_flow_monitor.clear()
        
        # Reset forensic log
        if hasattr(self, 'forensic_log'):
            self.forensic_log.clear()
        
        # Reset program state
        self.program_loaded = False
        self.program_entry_point = 0
        
        # Set up memory layout again
        self._setup_memory_layout(self.memory.size)
        
        # Apply memory protections
        self._apply_memory_protections()
        
        # Log reset
        self.forensic_log.log_system_event("reset", {})
    
    def handle_side_effects(
        self,
        processor: Processor,
        thread: Any,
        instruction: Instruction,
        side_effects: Dict[str, Any]
    ) -> None:
        """
        Handle instruction side effects with security monitoring.
        
        Args:
            processor: Processor that executed the instruction
            thread: Thread containing the instruction
            instruction: The instruction that was executed
            side_effects: Side effects from instruction execution
        """
        # Handle base side effects
        super().handle_side_effects(processor, thread, instruction, side_effects)
        
        # Handle security-specific side effects
        
        # Privilege changes
        if "privilege_change" in side_effects:
            change = side_effects["privilege_change"]
            
            # Log the privilege change
            self.forensic_log.log_privilege_change(
                change["previous_level"],
                change["new_level"],
                instruction.opcode,
                processor.registers.get_pc(),
                {"thread_id": thread.thread_id}
            )
        
        # Control flow events (call/ret)
        if "call" in side_effects:
            call = side_effects["call"]
            
            # Record the call in the control flow monitor
            if hasattr(self, 'control_flow_monitor'):
                self.control_flow_monitor.record_call(
                    processor.registers.get_pc() - len(instruction),
                    call["target"],
                    call["return_addr"],
                    instruction.opcode,
                    {"thread_id": thread.thread_id}
                )
        
        if "ret" in side_effects:
            ret = side_effects["ret"]
            
            # Record the return in the control flow monitor
            if hasattr(self, 'control_flow_monitor'):
                self.control_flow_monitor.record_return(
                    processor.registers.get_pc() - len(instruction),
                    ret["return_addr"],
                    instruction.opcode,
                    {
                        "thread_id": thread.thread_id,
                        "shadow_valid": ret.get("shadow_valid", True)
                    }
                )
    
    def schedule_threads(self) -> None:
        """Schedule threads to processors."""
        # This is a simple scheduler for the security VM
        # Generally there will only be one thread
        if not self.processors[0].is_busy() and self.ready_queue:
            thread_id = self.ready_queue.pop(0)
            if thread_id in self.threads:
                thread = self.threads[thread_id]
                self.processors[0].assign_thread(thread_id, thread.pc)
                thread.state = ProcessorState.RUNNING
                thread.processor_id = 0