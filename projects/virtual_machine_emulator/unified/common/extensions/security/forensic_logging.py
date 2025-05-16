"""
Forensic logging for security virtual machine.

This module provides forensic logging capabilities for security research,
allowing detailed tracking of VM execution for later analysis.
"""

import time
from typing import Dict, List, Optional, Any


class ForensicLogger:
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
    
    def export_logs(self, format_type: str = "dict") -> Any:
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
    
    def clear(self) -> None:
        """Clear all logs and reset the timer."""
        self.logs = []
        self.start_time = time.time()


class MemoryAccessLog:
    """Record of a memory access for forensic analysis."""
    
    def __init__(
        self,
        address: int,
        access_type: str,
        value: Optional[int] = None,
        instruction_pointer: Optional[int] = None,
        thread_id: Optional[str] = None,
        timestamp: float = 0.0,
        context: Optional[Dict[str, Any]] = None
    ):
        self.address = address
        self.access_type = access_type
        self.value = value
        self.instruction_pointer = instruction_pointer
        self.thread_id = thread_id
        self.timestamp = timestamp
        self.context = context
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the access log to a dictionary."""
        result = {
            "address": self.address,
            "access_type": self.access_type,
            "timestamp": self.timestamp,
        }
        if self.value is not None:
            result["value"] = self.value
        if self.instruction_pointer is not None:
            result["instruction_pointer"] = self.instruction_pointer
        if self.thread_id is not None:
            result["thread_id"] = self.thread_id
        if self.context:
            result["context"] = self.context
        return result


class ProtectionEvent:
    """Record of a memory protection event."""
    
    def __init__(
        self,
        address: int,
        access_type: str,
        current_permission: Any,
        required_permission: Any,
        instruction_pointer: int,
        thread_id: Optional[str] = None,
        timestamp: float = 0.0,
        context: Optional[Dict[str, Any]] = None
    ):
        self.address = address
        self.access_type = access_type
        self.current_permission = current_permission
        self.required_permission = required_permission
        self.instruction_pointer = instruction_pointer
        self.thread_id = thread_id
        self.timestamp = timestamp
        self.context = context
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the protection event to a dictionary."""
        result = {
            "address": self.address,
            "access_type": self.access_type,
            "current_permission": str(self.current_permission),
            "required_permission": str(self.required_permission),
            "instruction_pointer": self.instruction_pointer,
            "timestamp": self.timestamp,
        }
        if self.thread_id is not None:
            result["thread_id"] = self.thread_id
        if self.context:
            result["context"] = self.context
        return result