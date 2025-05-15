"""
Control flow integrity monitoring for the virtual machine emulator.

This module provides mechanisms for ensuring control flow integrity:
- Shadow stack for return address verification
- Control flow tracking and analysis
- Visualization of control flow patterns
- Detection of control flow hijacking attempts
"""

import time
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Union, Any, Callable

from common.core.exceptions import ProcessorException


class ControlFlowEventType(Enum):
    """Types of control flow events."""
    CALL = auto()          # Function call
    RETURN = auto()        # Function return
    JUMP = auto()          # Direct jump
    CONDITIONAL = auto()   # Conditional branch
    SYSCALL = auto()       # System call
    INTERRUPT = auto()     # Hardware interrupt
    EXCEPTION = auto()     # Exception handling
    PRIVILEGE = auto()     # Privilege level change


class ControlFlowRecord:
    """Record of a control flow event for integrity monitoring."""
    
    def __init__(
        self,
        from_address: int,
        to_address: int,
        event_type: str,
        instruction: str,
        legitimate: bool = True,
        context: Dict[str, Any] = None,
    ):
        """
        Initialize a control flow record.
        
        Args:
            from_address: Source address
            to_address: Destination address
            event_type: Type of control flow event
            instruction: Instruction that caused the event
            legitimate: Whether the control flow is legitimate
            context: Additional context information
        """
        self.from_address = from_address
        self.to_address = to_address
        self.event_type = event_type
        self.instruction = instruction
        self.legitimate = legitimate
        self.context = context or {}
        self.timestamp = time.time()
    
    def __str__(self) -> str:
        """Return a string representation of the control flow record."""
        return (
            f"Control flow: {self.event_type} from 0x{self.from_address:x} "
            f"to 0x{self.to_address:x} via {self.instruction} "
            f"{'(legitimate)' if self.legitimate else '(HIJACKED)'}"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the record to a dictionary."""
        result = {
            "from_address": self.from_address,
            "to_address": self.to_address,
            "event_type": self.event_type,
            "instruction": self.instruction,
            "legitimate": self.legitimate,
            "timestamp": self.timestamp,
        }
        
        if self.context:
            result["context"] = self.context
        
        return result


class ControlFlowException(ProcessorException):
    """Exception raised for control flow integrity violations."""
    
    def __init__(
        self,
        message: str,
        from_address: int,
        to_address: int,
        expected_address: Optional[int] = None,
    ):
        """
        Initialize a control flow exception.
        
        Args:
            message: Exception message
            from_address: Source address
            to_address: Actual destination address
            expected_address: Expected destination address if applicable
        """
        super().__init__(message)
        self.from_address = from_address
        self.to_address = to_address
        self.expected_address = expected_address
    
    def __str__(self) -> str:
        """Return a string representation of the exception."""
        if self.expected_address is not None:
            return (f"Control flow integrity violation: {self.message} "
                   f"(from 0x{self.from_address:x} to 0x{self.to_address:x}, "
                   f"expected 0x{self.expected_address:x})")
        else:
            return (f"Control flow integrity violation: {self.message} "
                   f"(from 0x{self.from_address:x} to 0x{self.to_address:x})")


class ShadowStack:
    """Shadow stack for control flow integrity monitoring."""
    
    def __init__(self, stack_size: int = 1024):
        """
        Initialize the shadow stack.
        
        Args:
            stack_size: Maximum shadow stack size
        """
        self.stack: List[int] = []
        self.max_size = stack_size
        self.call_sites: Dict[int, int] = {}  # Maps call site to target
        self.return_targets: Dict[int, Set[int]] = {}  # Maps return address to valid call sites
    
    def push(self, return_address: int, call_site: int, target: int) -> None:
        """
        Push a return address onto the shadow stack.
        
        Args:
            return_address: Return address to preserve
            call_site: Address of the call instruction
            target: Target of the call
            
        Raises:
            ControlFlowException: If the shadow stack overflows
        """
        if len(self.stack) >= self.max_size:
            raise ControlFlowException(
                "Shadow stack overflow",
                call_site,
                target
            )
        
        self.stack.append(return_address)
        
        # Record call site information for enhanced CFI
        self.call_sites[call_site] = target
        
        if return_address not in self.return_targets:
            self.return_targets[return_address] = set()
        
        self.return_targets[return_address].add(call_site)
    
    def pop(self) -> int:
        """
        Pop a return address from the shadow stack.
        
        Returns:
            The expected return address
            
        Raises:
            ControlFlowException: If the shadow stack is empty
        """
        if not self.stack:
            raise ControlFlowException(
                "Shadow stack underflow (return without matching call)",
                0,
                0
            )
        
        return self.stack.pop()
    
    def check_return(self, actual_return: int, current_address: int) -> bool:
        """
        Check if a return address matches the expected value.
        
        Args:
            actual_return: Actual return address
            current_address: Current instruction pointer
            
        Returns:
            True if the return address is valid, False otherwise
        """
        if not self.stack:
            return False
        
        expected_return = self.stack[-1]
        return expected_return == actual_return
    
    def is_valid_call(self, call_site: int, target: int) -> bool:
        """
        Check if a call target is valid for a given call site.
        
        Args:
            call_site: The address of the call instruction
            target: The target address of the call
            
        Returns:
            True if the call is valid, False otherwise
        """
        # If we've seen this call site before, check target consistency
        if call_site in self.call_sites:
            return self.call_sites[call_site] == target
        
        # New call site is always considered valid
        return True
    
    def check_return_edge(self, return_addr: int, call_site: int) -> bool:
        """
        Check if a return edge is valid.
        
        Args:
            return_addr: The return address
            call_site: The original call site
            
        Returns:
            True if the return edge is valid, False otherwise
        """
        if return_addr not in self.return_targets:
            return False
        
        return call_site in self.return_targets[return_addr]
    
    def clear(self) -> None:
        """Clear the shadow stack."""
        self.stack.clear()
        self.call_sites.clear()
        self.return_targets.clear()
    
    def get_depth(self) -> int:
        """Get the current shadow stack depth."""
        return len(self.stack)


class ControlFlowMonitor:
    """
    Monitor and analyze control flow integrity.
    
    This class manages control flow recording and analysis.
    """
    
    def __init__(self, enable_shadow_stack: bool = True):
        """
        Initialize the control flow monitor.
        
        Args:
            enable_shadow_stack: Whether to enable shadow stack protection
        """
        self.records: List[ControlFlowRecord] = []
        self.shadow_stack = ShadowStack() if enable_shadow_stack else None
        self.enable_shadow_stack = enable_shadow_stack
        
        # Control flow graph
        self.call_graph: Dict[int, Set[int]] = {}  # Maps call sites to targets
        self.return_graph: Dict[int, Set[int]] = {}  # Maps return addresses to call sites
    
    def record_control_flow(
        self,
        from_address: int,
        to_address: int,
        event_type: str,
        instruction: str,
        legitimate: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> ControlFlowRecord:
        """
        Record a control flow event.
        
        Args:
            from_address: Source address
            to_address: Destination address
            event_type: Type of control flow event
            instruction: Instruction that caused the event
            legitimate: Whether the control flow is legitimate
            context: Additional context information
            
        Returns:
            The created control flow record
        """
        record = ControlFlowRecord(
            from_address=from_address,
            to_address=to_address,
            event_type=event_type,
            instruction=instruction,
            legitimate=legitimate,
            context=context,
        )
        
        self.records.append(record)
        
        # Update control flow graph
        if event_type == "call":
            if from_address not in self.call_graph:
                self.call_graph[from_address] = set()
            self.call_graph[from_address].add(to_address)
        
        elif event_type == "return":
            if to_address not in self.return_graph:
                self.return_graph[to_address] = set()
            self.return_graph[to_address].add(from_address)
        
        return record
    
    def record_call(
        self,
        call_site: int,
        target: int,
        return_addr: int,
        instruction: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ControlFlowRecord:
        """
        Record a function call with shadow stack tracking.
        
        Args:
            call_site: Address of the call instruction
            target: Target address of the call
            return_addr: Return address for the call
            instruction: The call instruction
            context: Additional context information
            
        Returns:
            The created control flow record
        """
        legitimate = True
        
        # Validate call if shadow stack is enabled
        if self.enable_shadow_stack:
            legitimate = self.shadow_stack.is_valid_call(call_site, target)
            
            # Push the return address onto the shadow stack
            self.shadow_stack.push(return_addr, call_site, target)
        
        # Record the call
        return self.record_control_flow(
            from_address=call_site,
            to_address=target,
            event_type="call",
            instruction=instruction,
            legitimate=legitimate,
            context=context
        )
    
    def record_return(
        self,
        return_site: int,
        target: int,
        instruction: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ControlFlowRecord:
        """
        Record a function return with shadow stack checking.
        
        Args:
            return_site: Address of the return instruction
            target: Target address of the return
            instruction: The return instruction
            context: Additional context information
            
        Returns:
            The created control flow record
        """
        legitimate = True
        expected_return = None
        
        # Validate return if shadow stack is enabled
        if self.enable_shadow_stack:
            try:
                expected_return = self.shadow_stack.pop()
                legitimate = (expected_return == target)
                
                if not legitimate and context is None:
                    context = {}
                
                if not legitimate:
                    context["expected_return"] = expected_return
            except ControlFlowException:
                legitimate = False
                if context is None:
                    context = {}
                context["error"] = "Shadow stack underflow"
        
        # Record the return
        return self.record_control_flow(
            from_address=return_site,
            to_address=target,
            event_type="return",
            instruction=instruction,
            legitimate=legitimate,
            context=context
        )
    
    def clear(self) -> None:
        """Clear all control flow records and state."""
        self.records.clear()
        self.call_graph.clear()
        self.return_graph.clear()
        
        if self.shadow_stack:
            self.shadow_stack.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about recorded control flow.
        
        Returns:
            Dictionary of control flow statistics
        """
        # Count event types
        event_counts = {}
        legitimate_count = 0
        illegitimate_count = 0
        
        for record in self.records:
            event_counts[record.event_type] = event_counts.get(record.event_type, 0) + 1
            
            if record.legitimate:
                legitimate_count += 1
            else:
                illegitimate_count += 1
        
        return {
            "total_events": len(self.records),
            "legitimate_events": legitimate_count,
            "illegitimate_events": illegitimate_count,
            "event_types": event_counts,
            "unique_call_sites": len(self.call_graph),
            "unique_call_targets": sum(len(targets) for targets in self.call_graph.values()),
            "unique_return_sites": len(self.return_graph),
            "shadow_stack_depth": self.shadow_stack.get_depth() if self.shadow_stack else 0,
        }
    
    def get_control_flow_visualization(self, format_type: str = "dict") -> Union[Dict[str, Any], str]:
        """
        Generate a visualization of the control flow.
        
        Args:
            format_type: Output format ('dict' or 'json')
            
        Returns:
            Control flow visualization in the requested format
        """
        # Build a graph representation
        nodes = set()
        edges = []
        
        for record in self.records:
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