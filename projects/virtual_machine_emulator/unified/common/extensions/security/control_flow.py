"""
Control flow integrity extension for VM security.

This module provides mechanisms for tracking and enforcing control flow
integrity, including shadow stack protections and control flow monitoring.
"""

from __future__ import annotations
import time
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Union, Any, Callable

from common.core.processor import (
    Processor,
    ProcessorState,
    PrivilegeLevel,
    RegisterSet
)
from common.core.instruction import Instruction, InstructionType
from common.core.exceptions import (
    ProcessorException, 
    InvalidInstructionException, 
    PrivilegeViolationException
)


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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the control flow record to a dictionary."""
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


class ControlFlowIntegrityMonitor:
    """
    Control flow integrity monitor that tracks and validates program execution flow.
    
    This class provides mechanisms for monitoring control flow events, maintaining
    a shadow stack for return address validation, and detecting control flow hijacking.
    """
    
    def __init__(self, record_limit: int = 1000):
        """
        Initialize the control flow integrity monitor.
        
        Args:
            record_limit: Maximum number of control flow records to keep
        """
        self.control_flow_records: List[ControlFlowRecord] = []
        self.shadow_stack: List[int] = []  # For control flow integrity checking
        self.record_limit = record_limit
        self.legitimate_call_targets: Set[int] = set()  # Known valid call targets
        self.legitimate_branch_targets: Set[int] = set()  # Known valid branch targets
    
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
        Record a control flow event for integrity monitoring.
        
        Args:
            from_address: Source address
            to_address: Destination address
            event_type: Type of control flow event
            instruction: Instruction that caused the event
            legitimate: Whether the control flow is legitimate
            context: Additional context for the event
            
        Returns:
            The recorded control flow event
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
        
        # Limit the number of records to avoid excessive memory usage
        if len(self.control_flow_records) > self.record_limit:
            self.control_flow_records.pop(0)
            
        return record
    
    def push_shadow_stack(self, return_address: int) -> None:
        """
        Push a return address onto the shadow stack.
        
        Args:
            return_address: The return address to push
        """
        self.shadow_stack.append(return_address)
    
    def pop_shadow_stack(self) -> Optional[int]:
        """
        Pop a return address from the shadow stack.
        
        Returns:
            The popped return address, or None if the shadow stack is empty
        """
        if not self.shadow_stack:
            return None
        
        return self.shadow_stack.pop()
    
    def validate_return(self, actual_return: int) -> Tuple[bool, Optional[int]]:
        """
        Validate a return against the shadow stack.
        
        Args:
            actual_return: The actual return address used
            
        Returns:
            Tuple of (valid, expected_return_address)
        """
        if not self.shadow_stack:
            return False, None
        
        expected_return = self.shadow_stack.pop()
        return expected_return == actual_return, expected_return
    
    def register_valid_call_target(self, address: int) -> None:
        """
        Register a valid call target.
        
        Args:
            address: A valid call target address
        """
        self.legitimate_call_targets.add(address)
    
    def register_valid_branch_target(self, address: int) -> None:
        """
        Register a valid branch target.
        
        Args:
            address: A valid branch target address
        """
        self.legitimate_branch_targets.add(address)
    
    def validate_call_target(self, address: int) -> bool:
        """
        Validate a call target address.
        
        Args:
            address: The target address to validate
            
        Returns:
            Whether the address is a valid call target
        """
        # If no valid targets registered, all are considered valid
        if not self.legitimate_call_targets:
            return True
            
        return address in self.legitimate_call_targets
    
    def validate_branch_target(self, address: int) -> bool:
        """
        Validate a branch target address.
        
        Args:
            address: The target address to validate
            
        Returns:
            Whether the address is a valid branch target
        """
        # If no valid targets registered, all are considered valid
        if not self.legitimate_branch_targets:
            return True
            
        return address in self.legitimate_branch_targets
    
    def get_control_flow_records(self) -> List[ControlFlowRecord]:
        """
        Get all recorded control flow events.
        
        Returns:
            List of control flow records
        """
        return self.control_flow_records
    
    def get_control_flow_violations(self) -> List[ControlFlowRecord]:
        """
        Get all recorded control flow violations.
        
        Returns:
            List of control flow violation records
        """
        return [r for r in self.control_flow_records if not r.legitimate]
    
    def reset(self) -> None:
        """Reset the control flow monitor state."""
        self.control_flow_records = []
        self.shadow_stack = []


class ControlFlowVisualization:
    """
    Generates visualizations of control flow for analysis and reporting.
    """
    
    def __init__(self, control_flow_records: List[ControlFlowRecord]):
        """
        Initialize with control flow records.
        
        Args:
            control_flow_records: List of control flow records to visualize
        """
        self.records = control_flow_records
    
    def generate_graph(self) -> Dict[str, Any]:
        """
        Generate a graph representation of the control flow.
        
        Returns:
            Dictionary containing nodes and edges
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
        
        return {
            "nodes": nodes_list,
            "edges": edges,
        }
    
    def generate_sequence(self) -> List[Dict[str, Any]]:
        """
        Generate a sequential representation of the control flow.
        
        Returns:
            List of control flow events in sequence
        """
        return [record.to_dict() for record in self.records]
    
    def highlight_violations(self) -> List[Dict[str, Any]]:
        """
        Extract and highlight control flow violations.
        
        Returns:
            List of control flow violation records
        """
        violations = []
        
        for record in self.records:
            if not record.legitimate:
                violations.append(record.to_dict())
        
        return violations