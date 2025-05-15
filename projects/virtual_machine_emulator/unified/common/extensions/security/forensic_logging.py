"""
Forensic logging systems for the virtual machine emulator.

This module provides comprehensive logging and analysis capabilities:
- Detailed event logging
- Memory access tracking
- Protection violation records
- Security event reporting and analysis
"""

import time
import json
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Union, Any, BinaryIO, Callable


class LoggingLevel(Enum):
    """Logging detail level."""
    NONE = 0        # No logging
    MINIMAL = 1     # Basic events only
    STANDARD = 2    # Standard security events
    DETAILED = 3    # Detailed events with context
    MAXIMUM = 4     # Maximum detail including memory operations


class EventCategory(Enum):
    """Categories of forensic events."""
    SYSTEM = auto()       # System-level events
    MEMORY = auto()       # Memory-related events
    CONTROL_FLOW = auto() # Control flow events
    PROTECTION = auto()   # Security protection events
    EXECUTION = auto()    # Instruction execution events
    ATTACK = auto()       # Attack detection events
    PRIVILEGE = auto()    # Privilege-related events


class ForensicLog:
    """Forensic logging system for security analysis."""
    
    def __init__(
        self,
        enabled: bool = True,
        level: LoggingLevel = LoggingLevel.STANDARD,
        max_events: int = 10000,
    ):
        """
        Initialize the forensic logging system.
        
        Args:
            enabled: Whether logging is enabled
            level: Logging detail level
            max_events: Maximum number of events to store
        """
        self.enabled = enabled
        self.level = level
        self.max_events = max_events
        self.logs: List[Dict[str, Any]] = []
        self.start_time = time.time()
        
        # Category filters
        self.category_filters: Dict[EventCategory, bool] = {
            category: True for category in EventCategory
        }
        
        # Statistics
        self.event_counts: Dict[str, int] = {}
        self.category_counts: Dict[EventCategory, int] = {}
    
    def log_event(
        self,
        event_type: str,
        category: EventCategory,
        data: Dict[str, Any],
        timestamp: Optional[float] = None,
    ) -> None:
        """
        Log an event if logging is enabled and level is sufficient.
        
        Args:
            event_type: Type of event
            category: Event category
            data: Event data
            timestamp: Event timestamp (defaults to current time)
        """
        if not self.enabled:
            return
        
        # Check category filter
        if not self.category_filters.get(category, True):
            return
        
        # Check if we're at our event limit
        if len(self.logs) >= self.max_events:
            # Remove oldest event
            self.logs.pop(0)
        
        # Create the event entry
        entry = {
            "timestamp": timestamp or (time.time() - self.start_time),
            "event_type": event_type,
            "category": category.name,
            "data": data,
        }
        
        # Add to the log
        self.logs.append(entry)
        
        # Update statistics
        self.event_counts[event_type] = self.event_counts.get(event_type, 0) + 1
        self.category_counts[category] = self.category_counts.get(category, 0) + 1
    
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
            value: Value being written (for write operations)
            context: Additional context information
        """
        # Skip if not detailed logging
        if self.level.value < LoggingLevel.DETAILED.value:
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
        
        self.log_event("memory_access", EventCategory.MEMORY, data)
    
    def log_control_flow(self, event: Dict[str, Any]) -> None:
        """
        Log a control flow event.
        
        Args:
            event: Control flow event details
        """
        if self.level.value < LoggingLevel.STANDARD.value:
            return
        
        self.log_event("control_flow", EventCategory.CONTROL_FLOW, event)
    
    def log_protection_violation(self, event: Dict[str, Any]) -> None:
        """
        Log a protection violation event.
        
        Args:
            event: Protection violation details
        """
        # Always log protection violations (unless disabled)
        if not self.enabled:
            return
        
        self.log_event("protection_violation", EventCategory.PROTECTION, event)
    
    def log_system_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log a system-level event.
        
        Args:
            event_type: Type of system event
            details: Event details
        """
        if self.level.value < LoggingLevel.MINIMAL.value:
            return
        
        data = {"system_event": event_type, **details}
        self.log_event(event_type, EventCategory.SYSTEM, data)
    
    def log_attack_detection(
        self,
        attack_type: str,
        confidence: float,
        details: Dict[str, Any],
    ) -> None:
        """
        Log an attack detection event.
        
        Args:
            attack_type: Type of attack detected
            confidence: Confidence level (0.0-1.0)
            details: Attack details
        """
        # Always log attack detections (unless disabled)
        if not self.enabled:
            return
        
        data = {
            "attack_type": attack_type,
            "confidence": confidence,
            **details
        }
        
        self.log_event("attack_detection", EventCategory.ATTACK, data)
    
    def log_privilege_change(
        self,
        from_level: str,
        to_level: str,
        source: str,
        instruction_pointer: int,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log a privilege level change.
        
        Args:
            from_level: Original privilege level
            to_level: New privilege level
            source: Source of the change (instruction, syscall, etc.)
            instruction_pointer: Current instruction pointer
            details: Additional details
        """
        if self.level.value < LoggingLevel.STANDARD.value:
            return
        
        data = {
            "from_level": from_level,
            "to_level": to_level,
            "source": source,
            "instruction_pointer": instruction_pointer,
        }
        
        if details:
            data.update(details)
        
        self.log_event("privilege_change", EventCategory.PRIVILEGE, data)
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """
        Get all logged events.
        
        Returns:
            List of log events
        """
        return self.logs
    
    def export_logs(self, format_type: str = "dict") -> Union[List[Dict[str, Any]], str]:
        """
        Export logs in the specified format.
        
        Args:
            format_type: Export format (dict, json, or text)
            
        Returns:
            Logs in the requested format
            
        Raises:
            ValueError: If format type is unsupported
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
                category = log["category"]
                
                data_items = []
                for k, v in log["data"].items():
                    # Format the value based on type
                    if isinstance(v, int) and k.lower().endswith(("address", "pointer")):
                        data_items.append(f"{k}=0x{v:x}")
                    else:
                        data_items.append(f"{k}={v}")
                
                data_str = ", ".join(data_items)
                text_logs.append(f"[{timestamp:.6f}] {category}.{event_type}: {data_str}")
            
            return "\n".join(text_logs)
        else:
            raise ValueError(f"Unsupported export format: {format_type}")
    
    def filter_logs(
        self,
        categories: Optional[List[EventCategory]] = None,
        event_types: Optional[List[str]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Filter logs by various criteria.
        
        Args:
            categories: List of categories to include
            event_types: List of event types to include
            start_time: Start time filter
            end_time: End time filter
            
        Returns:
            Filtered list of log events
        """
        result = self.logs
        
        if categories:
            category_names = [c.name for c in categories]
            result = [e for e in result if e["category"] in category_names]
        
        if event_types:
            result = [e for e in result if e["event_type"] in event_types]
        
        if start_time is not None:
            result = [e for e in result if e["timestamp"] >= start_time]
        
        if end_time is not None:
            result = [e for e in result if e["timestamp"] <= end_time]
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about logged events.
        
        Returns:
            Dictionary with logging statistics
        """
        category_stats = {
            category.name: count 
            for category, count in self.category_counts.items()
        }
        
        return {
            "total_events": len(self.logs),
            "event_types": self.event_counts,
            "categories": category_stats,
            "logging_level": self.level.name,
            "enabled": self.enabled,
            "uptime": time.time() - self.start_time,
        }
    
    def clear(self) -> None:
        """Clear all logs."""
        self.logs.clear()
        self.event_counts.clear()
        self.category_counts.clear()
    
    def enable_category(self, category: EventCategory) -> None:
        """
        Enable logging for a specific category.
        
        Args:
            category: Category to enable
        """
        self.category_filters[category] = True
    
    def disable_category(self, category: EventCategory) -> None:
        """
        Disable logging for a specific category.
        
        Args:
            category: Category to disable
        """
        self.category_filters[category] = False
    
    def set_level(self, level: LoggingLevel) -> None:
        """
        Set the logging detail level.
        
        Args:
            level: New logging level
        """
        self.level = level
    
    def enable(self) -> None:
        """Enable logging."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable logging."""
        self.enabled = False


class ForensicAnalyzer:
    """
    Analyzer for forensic logs to detect security anomalies.
    """
    
    def __init__(self, forensic_log: ForensicLog):
        """
        Initialize the forensic analyzer.
        
        Args:
            forensic_log: Forensic log to analyze
        """
        self.log = forensic_log
    
    def detect_control_flow_anomalies(self) -> List[Dict[str, Any]]:
        """
        Detect control flow anomalies in the logs.
        
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Filter for control flow events
        control_flow_events = self.log.filter_logs(
            categories=[EventCategory.CONTROL_FLOW]
        )
        
        # Look for illegitimate control flow
        for event in control_flow_events:
            data = event["data"]
            if data.get("legitimate") is False:
                anomaly = {
                    "type": "illegitimate_control_flow",
                    "timestamp": event["timestamp"],
                    "event_type": data.get("event_type", "unknown"),
                    "from_address": data.get("from_address", 0),
                    "to_address": data.get("to_address", 0),
                    "instruction": data.get("instruction", "unknown"),
                    "expected": data.get("expected_return", 0),
                    "severity": "critical"
                }
                
                anomalies.append(anomaly)
        
        return anomalies
    
    def detect_memory_protection_violations(self) -> List[Dict[str, Any]]:
        """
        Detect memory protection violations in the logs.
        
        Returns:
            List of detected violations
        """
        violations = []
        
        # Filter for protection violation events
        protection_events = self.log.filter_logs(
            categories=[EventCategory.PROTECTION]
        )
        
        for event in protection_events:
            data = event["data"]
            
            violation = {
                "type": "memory_protection_violation",
                "timestamp": event["timestamp"],
                "address": data.get("address", 0),
                "access_type": data.get("access_type", "unknown"),
                "current_permission": data.get("current_permission", "unknown"),
                "required_permission": data.get("required_permission", "unknown"),
                "instruction_pointer": data.get("instruction_pointer", 0),
                "severity": "high"
            }
            
            violations.append(violation)
        
        return violations
    
    def detect_privilege_escalation(self) -> List[Dict[str, Any]]:
        """
        Detect privilege escalation in the logs.
        
        Returns:
            List of detected privilege escalations
        """
        escalations = []
        
        # Filter for privilege change events
        privilege_events = self.log.filter_logs(
            categories=[EventCategory.PRIVILEGE],
            event_types=["privilege_change"]
        )
        
        for event in privilege_events:
            data = event["data"]
            
            from_level = data.get("from_level", "")
            to_level = data.get("to_level", "")
            
            # Check if this is an escalation
            if self._is_privilege_escalation(from_level, to_level):
                escalation = {
                    "type": "privilege_escalation",
                    "timestamp": event["timestamp"],
                    "from_level": from_level,
                    "to_level": to_level,
                    "source": data.get("source", "unknown"),
                    "instruction_pointer": data.get("instruction_pointer", 0),
                    "severity": "critical"
                }
                
                escalations.append(escalation)
        
        return escalations
    
    def _is_privilege_escalation(self, from_level: str, to_level: str) -> bool:
        """
        Check if a privilege change is an escalation.
        
        Args:
            from_level: Original privilege level
            to_level: New privilege level
            
        Returns:
            True if this is an escalation, False otherwise
        """
        # Map privilege levels to numeric values
        level_map = {
            "USER": 0,
            "SUPERVISOR": 1,
            "KERNEL": 2
        }
        
        # Get numeric values
        from_value = level_map.get(from_level.upper(), -1)
        to_value = level_map.get(to_level.upper(), -1)
        
        # Check if this is an escalation
        return from_value < to_value
    
    def generate_security_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive security report from the logs.
        
        Returns:
            Security report dictionary
        """
        # Get statistics
        stats = self.log.get_statistics()
        
        # Detect anomalies
        control_flow_anomalies = self.detect_control_flow_anomalies()
        memory_violations = self.detect_memory_protection_violations()
        privilege_escalations = self.detect_privilege_escalation()
        
        # Build report
        report = {
            "timestamp": time.time(),
            "uptime": stats["uptime"],
            "event_count": stats["total_events"],
            "anomalies": {
                "control_flow": control_flow_anomalies,
                "memory_protection": memory_violations,
                "privilege_escalation": privilege_escalations,
                "total": len(control_flow_anomalies) + len(memory_violations) + len(privilege_escalations)
            },
            "statistics": stats,
            "risk_assessment": self._assess_risk(
                control_flow_anomalies,
                memory_violations,
                privilege_escalations
            )
        }
        
        return report
    
    def _assess_risk(
        self,
        control_flow_anomalies: List[Dict[str, Any]],
        memory_violations: List[Dict[str, Any]],
        privilege_escalations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess security risk based on detected anomalies.
        
        Args:
            control_flow_anomalies: Detected control flow anomalies
            memory_violations: Detected memory violations
            privilege_escalations: Detected privilege escalations
            
        Returns:
            Risk assessment dictionary
        """
        # Calculate risk scores
        control_flow_score = len(control_flow_anomalies) * 10
        memory_score = len(memory_violations) * 8
        privilege_score = len(privilege_escalations) * 15
        
        total_score = control_flow_score + memory_score + privilege_score
        
        # Determine risk level
        risk_level = "low"
        if total_score > 50:
            risk_level = "critical"
        elif total_score > 30:
            risk_level = "high"
        elif total_score > 10:
            risk_level = "medium"
        
        # Generate risk assessment
        assessment = {
            "risk_level": risk_level,
            "risk_score": total_score,
            "component_scores": {
                "control_flow": control_flow_score,
                "memory_protection": memory_score,
                "privilege_escalation": privilege_score
            },
            "recommendations": self._generate_recommendations(
                risk_level,
                bool(control_flow_anomalies),
                bool(memory_violations),
                bool(privilege_escalations)
            )
        }
        
        return assessment
    
    def _generate_recommendations(
        self,
        risk_level: str,
        has_control_flow_issues: bool,
        has_memory_issues: bool,
        has_privilege_issues: bool
    ) -> List[str]:
        """
        Generate security recommendations based on findings.
        
        Args:
            risk_level: Overall risk level
            has_control_flow_issues: Whether control flow issues were detected
            has_memory_issues: Whether memory issues were detected
            has_privilege_issues: Whether privilege issues were detected
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Add general recommendations based on risk level
        if risk_level in ("critical", "high"):
            recommendations.append("Immediate investigation required")
            recommendations.append("Consider terminating the virtual machine")
        
        # Add specific recommendations based on issue type
        if has_control_flow_issues:
            recommendations.append("Enable control flow integrity protection")
            recommendations.append("Implement shadow stack for return address verification")
        
        if has_memory_issues:
            recommendations.append("Enable data execution prevention (DEP)")
            recommendations.append("Implement stack canaries")
            recommendations.append("Consider enabling address space layout randomization (ASLR)")
        
        if has_privilege_issues:
            recommendations.append("Review privilege management")
            recommendations.append("Enforce strict privilege transition controls")
            recommendations.append("Implement privilege level monitoring")
        
        return recommendations