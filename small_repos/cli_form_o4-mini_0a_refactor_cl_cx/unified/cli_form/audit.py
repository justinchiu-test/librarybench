"""
Audit Logging for cli_form

This module provides audit logging functionality for tracking form interactions
and changes for compliance and debugging.
"""

import json
import os
import time
import datetime
import threading
import logging
from enum import Enum


class AuditLogLevel(Enum):
    """Log levels for audit events."""
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'


class AuditLogger:
    """Logger for capturing and storing audit events."""
    
    def __init__(self, log_file=None, console=False, compliance_mode=False):
        """
        Initialize the audit logger.
        
        Args:
            log_file (str, optional): Path to the audit log file
            console (bool): Whether to log to console
            compliance_mode (bool): Enable strict compliance mode
        """
        self.log_file = log_file
        self.console = console
        self.compliance_mode = compliance_mode
        self.entries = []
        self.lock = threading.Lock()
        
        # Set up Python logging for file output
        if log_file:
            self.logger = logging.getLogger('cli_form.audit')
            self.logger.setLevel(logging.INFO)
            
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
            if console:
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
    
    def log(self, action, user=None, field=None, value=None, success=None, 
            error=None, level=AuditLogLevel.INFO, metadata=None):
        """
        Log an audit event.
        
        Args:
            action (str): The action being performed
            user (str, optional): User identifier
            field (str, optional): Form field name
            value (any, optional): Field value (sensitive values will be masked)
            success (bool, optional): Whether the action succeeded
            error (str, optional): Error message if failed
            level (AuditLogLevel): Severity level
            metadata (dict, optional): Additional metadata
            
        Returns:
            dict: The logged entry
        """
        timestamp = datetime.datetime.now().isoformat()
        
        entry = {
            'timestamp': timestamp,
            'action': action,
            'level': level.value if isinstance(level, AuditLogLevel) else level
        }
        
        if user:
            entry['user'] = user
            
        if field:
            entry['field'] = field
            
        if value is not None:
            # Mask sensitive values in compliance mode
            if self.compliance_mode and field and any(s in field.lower() for s in 
                                                    ['password', 'secret', 'token', 'key', 'ssn', 'social']):
                entry['value'] = '*****'
            else:
                entry['value'] = value
                
        if success is not None:
            entry['success'] = success
            
        if error:
            entry['error'] = error
            
        if metadata:
            entry['metadata'] = metadata
            
        # Thread-safe log recording
        with self.lock:
            self.entries.append(entry)
            
            # Write to log file if configured
            if hasattr(self, 'logger'):
                log_message = f"{action}"
                if field:
                    log_message += f" | Field: {field}"
                if success is not None:
                    log_message += f" | Success: {success}"
                if error:
                    log_message += f" | Error: {error}"
                
                if level == AuditLogLevel.ERROR or level == 'ERROR':
                    self.logger.error(log_message)
                elif level == AuditLogLevel.WARNING or level == 'WARNING':
                    self.logger.warning(log_message)
                elif level == AuditLogLevel.CRITICAL or level == 'CRITICAL':
                    self.logger.critical(log_message)
                else:
                    self.logger.info(log_message)
            
            # Console logging if enabled and no logger configured
            elif self.console and not hasattr(self, 'logger'):
                print(f"[AUDIT] {timestamp} | {action}" + 
                     (f" | Field: {field}" if field else "") +
                     (f" | Success: {success}" if success is not None else "") +
                     (f" | Error: {error}" if error else ""))
                     
        return entry
    
    def get_logs(self, filter_action=None, filter_field=None, filter_success=None):
        """
        Get filtered audit logs.
        
        Args:
            filter_action (str, optional): Filter by action
            filter_field (str, optional): Filter by field name
            filter_success (bool, optional): Filter by success status
            
        Returns:
            list: Filtered log entries
        """
        with self.lock:
            if not any([filter_action, filter_field, filter_success is not None]):
                return self.entries.copy()
                
            filtered = []
            for entry in self.entries:
                matches = True
                
                if filter_action and entry.get('action') != filter_action:
                    matches = False
                if filter_field and entry.get('field') != filter_field:
                    matches = False
                if filter_success is not None and entry.get('success') != filter_success:
                    matches = False
                    
                if matches:
                    filtered.append(entry)
                    
            return filtered
    
    def export_logs(self, file_path, format='json'):
        """
        Export audit logs to a file.
        
        Args:
            file_path (str): Path to the export file
            format (str): Export format ('json' only for now)
            
        Returns:
            bool: True if successful
        """
        if format.lower() != 'json':
            raise ValueError("Only JSON export format is supported")
            
        with self.lock:
            with open(file_path, 'w') as f:
                json.dump(self.entries, f, indent=2)
                
        return True
    
    def clear(self):
        """
        Clear all audit logs.
        
        Returns:
            int: Number of entries cleared
        """
        with self.lock:
            count = len(self.entries)
            self.entries = []
        return count


# Global audit logger instance
_audit_logger = None


def init_audit_log(log_file=None, console=False, compliance_mode=False):
    """
    Initialize the global audit logger.
    
    Args:
        log_file (str, optional): Path to the audit log file
        console (bool): Whether to log to console
        compliance_mode (bool): Enable strict compliance mode
        
    Returns:
        AuditLogger: The configured audit logger
    """
    global _audit_logger
    _audit_logger = AuditLogger(log_file, console, compliance_mode)
    return _audit_logger


def audit_log(action, user=None, field=None, value=None, success=None, 
              error=None, level=AuditLogLevel.INFO, metadata=None):
    """
    Log an audit event to the global audit logger.
    
    Args:
        action (str): The action being performed
        user (str, optional): User identifier
        field (str, optional): Form field name
        value (any, optional): Field value (sensitive values will be masked)
        success (bool, optional): Whether the action succeeded
        error (str, optional): Error message if failed
        level (AuditLogLevel): Severity level
        metadata (dict, optional): Additional metadata
        
    Returns:
        dict: The logged entry
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(console=True)
        
    return _audit_logger.log(
        action, user, field, value, success, error, level, metadata
    )


def get_audit_logs(filter_action=None, filter_field=None, filter_success=None):
    """
    Get filtered audit logs from the global audit logger.
    
    Args:
        filter_action (str, optional): Filter by action
        filter_field (str, optional): Filter by field name
        filter_success (bool, optional): Filter by success status
        
    Returns:
        list: Filtered log entries
    """
    global _audit_logger
    if _audit_logger is None:
        return []
        
    return _audit_logger.get_logs(filter_action, filter_field, filter_success)


def export_audit_logs(file_path, format='json'):
    """
    Export audit logs from the global audit logger.
    
    Args:
        file_path (str): Path to the export file
        format (str): Export format ('json' only for now)
        
    Returns:
        bool: True if successful
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
        
    return _audit_logger.export_logs(file_path, format)


def clear_audit_logs():
    """
    Clear all audit logs from the global audit logger.
    
    Returns:
        int: Number of entries cleared
    """
    global _audit_logger
    if _audit_logger is None:
        return 0
        
    return _audit_logger.clear()