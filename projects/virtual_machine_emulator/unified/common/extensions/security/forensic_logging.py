"""
Forensic logging extension for VM security.

This module provides a robust forensic logging system for recording
and analyzing security events within the virtual machine.
"""

from __future__ import annotations
import time
import json
from typing import Dict, List, Optional, Set, Tuple, Union, Any, Callable, BinaryIO

from common.extensions.security.control_flow import ControlFlowRecord


class ForensicLog:
    """Forensic logging system for security monitoring."""
    
    def __init__(self, enabled: bool = True, detailed: bool = False):
        """
        Initialize the forensic logging system.
        
        Args:
            enabled: Whether logging is enabled
            detailed: Whether to log detailed events
        """
        self.enabled = enabled
        self.detailed = detailed
        self.logs: List[Dict[str, Any]] = []
        self.start_time = time.time()
    
    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Log an event if logging is enabled.
        
        Args:
            event_type: Type of event
            data: Event data
        """
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
        """
        Log a memory access event.
        
        Args:
            address: Memory address
            access_type: Type of access (read, write, execute)
            size: Size of access in bytes
            value: Optional value for writes
            context: Additional context for the access
        """
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
    
    def log_control_flow(self, event: Union[Dict[str, Any], ControlFlowRecord]) -> None:
        """
        Log a control flow event.
        
        Args:
            event: Control flow event or record
        """
        if not self.enabled:
            return
        
        # Convert ControlFlowRecord to dict if needed
        if isinstance(event, ControlFlowRecord):
            event_dict = event.to_dict()
        else:
            event_dict = event
            
        self.log_event("control_flow", event_dict)
    
    def log_protection_violation(self, event: Dict[str, Any]) -> None:
        """
        Log a protection violation event.
        
        Args:
            event: Protection violation event
        """
        if not self.enabled:
            return
        
        self.log_event("protection_violation", event)
    
    def log_system_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log a system-level event.
        
        Args:
            event_type: Type of system event
            details: Event details
        """
        if not self.enabled:
            return
        
        data = {"system_event": event_type, **details}
        self.log_event("system", data)
    
    def log_vulnerability(self, vuln_type: str, details: Dict[str, Any]) -> None:
        """
        Log a vulnerability-related event.
        
        Args:
            vuln_type: Type of vulnerability
            details: Vulnerability details
        """
        if not self.enabled:
            return
        
        data = {"vulnerability_type": vuln_type, **details}
        self.log_event("vulnerability", data)
    
    def log_attack(self, attack_type: str, success: bool, details: Dict[str, Any]) -> None:
        """
        Log an attack attempt.
        
        Args:
            attack_type: Type of attack
            success: Whether the attack was successful
            details: Attack details
        """
        if not self.enabled:
            return
        
        data = {
            "attack_type": attack_type,
            "success": success,
            **details
        }
        self.log_event("attack", data)
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """
        Get all logged events.
        
        Returns:
            List of log entries
        """
        return self.logs
    
    def export_logs(self, format_type: str = "dict") -> Union[List[Dict[str, Any]], str]:
        """
        Export logs in the specified format.
        
        Args:
            format_type: Format to export logs in (dict, json, text)
            
        Returns:
            Logs in the requested format
        """
        if format_type == "dict":
            return self.logs
        elif format_type == "json":
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
    
    def clear_logs(self) -> None:
        """Clear all logged events."""
        self.logs = []
    
    def filter_logs(
        self,
        event_types: Optional[List[str]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter logs based on specified criteria.
        
        Args:
            event_types: Types of events to include
            start_time: Start time for filtering
            end_time: End time for filtering
            filter_fn: Custom filter function
            
        Returns:
            Filtered list of log entries
        """
        filtered = self.logs
        
        # Filter by event types
        if event_types:
            filtered = [log for log in filtered if log["event_type"] in event_types]
        
        # Filter by time range
        if start_time is not None:
            filtered = [log for log in filtered if log["timestamp"] >= start_time]
        if end_time is not None:
            filtered = [log for log in filtered if log["timestamp"] <= end_time]
        
        # Apply custom filter
        if filter_fn:
            filtered = [log for log in filtered if filter_fn(log)]
        
        return filtered


class ForensicReport:
    """Generates security reports based on forensic logs."""
    
    def __init__(self, logs: ForensicLog):
        """
        Initialize with forensic logs.
        
        Args:
            logs: Forensic log instance to analyze
        """
        self.logs = logs
    
    def generate_summary(self) -> Dict[str, Any]:
        """
        Generate a summary report of security events.
        
        Returns:
            Security event summary
        """
        logs = self.logs.get_logs()
        
        # Count events by type
        event_counts = {}
        for log in logs:
            event_type = log["event_type"]
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Find protection violations
        protection_violations = [log for log in logs if log["event_type"] == "protection_violation"]
        
        # Find control flow violations
        control_flow_logs = [log for log in logs if log["event_type"] == "control_flow"]
        control_flow_violations = [log for log in control_flow_logs 
                                 if "legitimate" in log["data"] and not log["data"]["legitimate"]]
        
        # Find attack logs
        attack_logs = [log for log in logs if log["event_type"] == "attack"]
        successful_attacks = [log for log in attack_logs if log["data"]["success"]]
        
        return {
            "total_events": len(logs),
            "event_counts": event_counts,
            "protection_violations": len(protection_violations),
            "control_flow_violations": len(control_flow_violations),
            "attack_attempts": len(attack_logs),
            "successful_attacks": len(successful_attacks),
            "time_period": {
                "start": logs[0]["timestamp"] if logs else 0,
                "end": logs[-1]["timestamp"] if logs else 0,
            }
        }
    
    def get_memory_access_pattern(self) -> Dict[str, Dict[int, int]]:
        """
        Analyze memory access patterns from the forensic logs.
        
        Returns:
            Memory access pattern statistics
        """
        if not self.logs.detailed:
            return {"error": "Detailed logging must be enabled for memory access patterns"}
        
        patterns = {
            "read": {},
            "write": {},
            "execute": {},
        }
        
        for log in self.logs.get_logs():
            if log["event_type"] == "memory_access":
                access_type = log["data"]["access_type"]
                address = log["data"]["address"]
                
                if access_type in patterns:
                    patterns[access_type][address] = patterns[access_type].get(address, 0) + 1
        
        return patterns
    
    def get_control_flow_graph(self) -> Dict[str, Any]:
        """
        Generate a control flow graph from logged events.
        
        Returns:
            Control flow graph data
        """
        # Extract control flow records
        control_flow_logs = [log for log in self.logs.get_logs() if log["event_type"] == "control_flow"]
        
        # Build a graph representation
        nodes = set()
        edges = []
        
        for log in control_flow_logs:
            data = log["data"]
            from_addr = data.get("from_address")
            to_addr = data.get("to_address")
            
            if from_addr is not None and to_addr is not None:
                nodes.add(from_addr)
                nodes.add(to_addr)
                
                edge = {
                    "source": from_addr,
                    "target": to_addr,
                    "type": data.get("event_type", "unknown"),
                    "legitimate": data.get("legitimate", True),
                    "instruction": data.get("instruction", "unknown"),
                }
                edges.append(edge)
        
        nodes_list = [{"address": addr} for addr in sorted(nodes)]
        
        return {
            "nodes": nodes_list,
            "edges": edges,
        }