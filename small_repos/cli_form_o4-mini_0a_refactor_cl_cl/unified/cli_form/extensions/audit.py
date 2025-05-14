"""
Audit logging for the CLI Form Library.
"""
import time
from datetime import datetime
import typing as t


class AuditLog:
    """
    Audit logging system to track form usage.
    """
    
    def __init__(self):
        """Initialize an empty audit log."""
        self._entries = []
        
    def record(self, action: str, user: t.Optional[str] = None, details: t.Optional[t.Dict[str, t.Any]] = None) -> None:
        """
        Record an action in the audit log.
        
        Args:
            action: The action being performed
            user: Optional user identifier
            details: Optional additional details
        """
        entry = {
            "timestamp": datetime.now(),
            "time": time.time(),
            "action": action
        }
        
        if user:
            entry["user"] = user
            
        if details:
            entry.update(details)
            
        self._entries.append(entry)
        
    def get_logs(self) -> t.List[t.Dict[str, t.Any]]:
        """
        Get all audit log entries.
        
        Returns:
            List of audit log entries
        """
        return self._entries
        
    def get_log(self) -> t.List[t.Dict[str, t.Any]]:
        """Alternative name for get_logs."""
        return self.get_logs()
        
    def clear(self) -> None:
        """Clear all audit log entries."""
        self._entries = []