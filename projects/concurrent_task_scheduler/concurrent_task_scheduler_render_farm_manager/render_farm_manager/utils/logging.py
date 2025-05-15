"""Logging and monitoring utilities for the Render Farm Manager."""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

from render_farm_manager.core.interfaces import AuditInterface
from render_farm_manager.core.models import AuditLogEntry


class AuditLogger(AuditInterface):
    """Implementation of the audit logger for tracking render farm activity."""
    
    def __init__(self):
        """Initialize the audit logger."""
        self.logs: List[AuditLogEntry] = []
        self.logger = logging.getLogger("render_farm.audit")
        
    def log_event(self, event_type: str, description: str, **details) -> AuditLogEntry:
        """
        Log an event in the audit trail.
        
        Args:
            event_type: Type of event
            description: Human-readable description of the event
            **details: Additional details about the event
            
        Returns:
            The created audit log entry
        """
        entry = AuditLogEntry(
            timestamp=datetime.now(),
            event_type=event_type,
            description=description,
            details=details,
            job_id=details.get("job_id"),
            node_id=details.get("node_id"),
            client_id=details.get("client_id"),
        )
        
        self.logs.append(entry)
        self.logger.info(
            f"{entry.timestamp} - {event_type}: {description} "
            f"(job_id={entry.job_id}, node_id={entry.node_id}, client_id={entry.client_id})"
        )
        
        return entry
    
    def get_job_history(self, job_id: str) -> List[AuditLogEntry]:
        """
        Get the audit history for a specific job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            List of audit log entries related to the job
        """
        return [entry for entry in self.logs if entry.job_id == job_id]
    
    def get_node_history(self, node_id: str) -> List[AuditLogEntry]:
        """
        Get the audit history for a specific node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            List of audit log entries related to the node
        """
        return [entry for entry in self.logs if entry.node_id == node_id]
    
    def get_client_history(self, client_id: str) -> List[AuditLogEntry]:
        """
        Get the audit history for a specific client.
        
        Args:
            client_id: ID of the client
            
        Returns:
            List of audit log entries related to the client
        """
        return [entry for entry in self.logs if entry.client_id == client_id]
    
    def get_logs_by_time_range(self, start_time: datetime, end_time: datetime) -> List[AuditLogEntry]:
        """
        Get logs within a specific time range.
        
        Args:
            start_time: Start of the time range
            end_time: End of the time range
            
        Returns:
            List of audit log entries within the time range
        """
        return [
            entry for entry in self.logs 
            if start_time <= entry.timestamp <= end_time
        ]
    
    def get_logs_by_event_type(self, event_type: str) -> List[AuditLogEntry]:
        """
        Get logs of a specific event type.
        
        Args:
            event_type: The event type to filter by
            
        Returns:
            List of audit log entries with the specified event type
        """
        return [entry for entry in self.logs if entry.event_type == event_type]


class PerformanceMonitor:
    """Monitor and track performance metrics for the render farm."""
    
    def __init__(self, audit_logger: AuditLogger):
        """
        Initialize the performance monitor.
        
        Args:
            audit_logger: The audit logger to record performance events
        """
        self.audit_logger = audit_logger
        self.operation_times: Dict[str, List[float]] = {}
        self.client_metrics: Dict[str, Dict[str, float]] = {}
        
    def time_operation(self, operation_name: str) -> 'TimedOperation':
        """
        Create a context manager to time an operation.
        
        Args:
            operation_name: Name of the operation to time
            
        Returns:
            A context manager for timing the operation
        """
        return TimedOperation(self, operation_name)
    
    def record_operation_time(self, operation_name: str, duration_ms: float) -> None:
        """
        Record the time taken for an operation.
        
        Args:
            operation_name: Name of the operation
            duration_ms: Duration of the operation in milliseconds
        """
        if operation_name not in self.operation_times:
            self.operation_times[operation_name] = []
        
        self.operation_times[operation_name].append(duration_ms)
        
        self.audit_logger.log_event(
            "performance_metric",
            f"Operation '{operation_name}' completed in {duration_ms:.2f}ms",
            operation_name=operation_name,
            duration_ms=duration_ms,
        )
    
    def update_client_resource_metrics(self, client_id: str, allocated_percentage: float, 
                                      borrowed_percentage: float = 0.0, lent_percentage: float = 0.0) -> None:
        """
        Update resource metrics for a client.
        
        Args:
            client_id: ID of the client
            allocated_percentage: Percentage of resources allocated to the client
            borrowed_percentage: Percentage of resources borrowed from other clients
            lent_percentage: Percentage of resources lent to other clients
        """
        if client_id not in self.client_metrics:
            self.client_metrics[client_id] = {}
            
        self.client_metrics[client_id].update({
            "allocated_percentage": allocated_percentage,
            "borrowed_percentage": borrowed_percentage,
            "lent_percentage": lent_percentage,
        })
        
        self.audit_logger.log_event(
            "client_resource_metrics_updated",
            f"Client {client_id} resource metrics updated: allocated={allocated_percentage:.2f}%, "
            f"borrowed={borrowed_percentage:.2f}%, lent={lent_percentage:.2f}%",
            client_id=client_id,
            allocated_percentage=allocated_percentage,
            borrowed_percentage=borrowed_percentage,
            lent_percentage=lent_percentage,
        )
    
    def update_energy_cost_saved(self, amount: float, mode: str) -> None:
        """
        Update the amount of energy cost saved.
        
        Args:
            amount: Amount of cost saved
            mode: Energy mode that enabled the savings
        """
        self.audit_logger.log_event(
            "energy_cost_savings",
            f"Energy cost savings recorded: {amount:.2f} in {mode} mode",
            amount=amount,
            mode=mode,
        )
    
    def get_average_operation_time(self, operation_name: str) -> Optional[float]:
        """
        Get the average time for an operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Average time in milliseconds, or None if no data is available
        """
        if operation_name not in self.operation_times or not self.operation_times[operation_name]:
            return None
        
        return sum(self.operation_times[operation_name]) / len(self.operation_times[operation_name])
    
    def get_max_operation_time(self, operation_name: str) -> Optional[float]:
        """
        Get the maximum time for an operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Maximum time in milliseconds, or None if no data is available
        """
        if operation_name not in self.operation_times or not self.operation_times[operation_name]:
            return None
        
        return max(self.operation_times[operation_name])
    
    def get_min_operation_time(self, operation_name: str) -> Optional[float]:
        """
        Get the minimum time for an operation.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Minimum time in milliseconds, or None if no data is available
        """
        if operation_name not in self.operation_times or not self.operation_times[operation_name]:
            return None
        
        return min(self.operation_times[operation_name])
    
    def get_client_metrics(self, client_id: str) -> Dict[str, float]:
        """
        Get resource metrics for a client.
        
        Args:
            client_id: ID of the client
            
        Returns:
            Dictionary of resource metrics for the client
        """
        return self.client_metrics.get(client_id, {})
    
    def reset_metrics(self) -> None:
        """Reset all performance metrics."""
        self.operation_times = {}
        self.client_metrics = {}


class TimedOperation:
    """Context manager for timing operations."""
    
    def __init__(self, monitor: PerformanceMonitor, operation_name: str):
        """
        Initialize the timed operation.
        
        Args:
            monitor: The performance monitor
            operation_name: Name of the operation to time
        """
        self.monitor = monitor
        self.operation_name = operation_name
        self.start_time = 0.0
        
    def __enter__(self) -> 'TimedOperation':
        """Start timing the operation."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Stop timing the operation and record the duration.
        
        Args:
            exc_type: Exception type, if an exception was raised
            exc_val: Exception value, if an exception was raised
            exc_tb: Exception traceback, if an exception was raised
        """
        end_time = time.time()
        duration_ms = (end_time - self.start_time) * 1000
        self.monitor.record_operation_time(self.operation_name, duration_ms)