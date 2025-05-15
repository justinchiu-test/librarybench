"""Audit logging for query language interpreters."""

import logging
import hmac
import hashlib
import json
from typing import Any, Dict, List, Optional, Set, Union
from datetime import datetime

from common.logging.base import BaseLogger, LogLevel


class AuditLogger(BaseLogger):
    """Logger for audit events."""

    def __init__(
        self,
        name: str,
        log_file: str,
        hmac_key: Optional[str] = None,
        console: bool = False,
        level: str = LogLevel.INFO,
    ):
        """Initialize an audit logger.

        Args:
            name: Logger name
            log_file: Path to audit log file
            hmac_key: Key for HMAC signature (None for no signature)
            console: Whether to log to console
            level: Minimum log level
        """
        super().__init__(name, log_file, console, level)
        self.hmac_key = hmac_key.encode('utf-8') if hmac_key else None

    def _create_signature(self, data: str) -> str:
        """Create HMAC signature for audit log entry.

        Args:
            data: Data to sign

        Returns:
            str: HMAC signature
        """
        if not self.hmac_key:
            return ""
        
        h = hmac.new(self.hmac_key, data.encode('utf-8'), hashlib.sha256)
        return h.hexdigest()

    def audit(
        self,
        action: str,
        user: str,
        resource: str,
        status: str = "success",
        **details
    ) -> None:
        """Log an audit event.

        Args:
            action: Action being performed
            user: User performing the action
            resource: Resource being accessed
            status: Status of the action
            **details: Additional audit details
        """
        timestamp = datetime.now().isoformat()
        
        # Create audit entry
        audit_entry = {
            "timestamp": timestamp,
            "action": action,
            "user": user,
            "resource": resource,
            "status": status,
        }
        
        # Add details
        if details:
            audit_entry["details"] = details
        
        # Convert to JSON
        audit_json = json.dumps(audit_entry)
        
        # Add signature if hmac_key is provided
        if self.hmac_key:
            signature = self._create_signature(audit_json)
            audit_entry["signature"] = signature
            audit_json = json.dumps(audit_entry)
        
        # Log the audit entry
        self.logger.info(audit_json)

    def verify_integrity(self, audit_entry: str) -> bool:
        """Verify the integrity of an audit log entry.

        Args:
            audit_entry: Audit log entry to verify

        Returns:
            bool: True if entry is valid, False otherwise
        """
        if not self.hmac_key:
            return True  # No integrity check if no hmac_key
        
        try:
            # Parse the audit entry
            entry_data = json.loads(audit_entry)
            
            # Extract the signature
            signature = entry_data.pop("signature", None)
            if not signature:
                return False
            
            # Re-create JSON without signature
            entry_json = json.dumps(entry_data)
            
            # Verify signature
            expected_signature = self._create_signature(entry_json)
            return hmac.compare_digest(signature, expected_signature)
        
        except (json.JSONDecodeError, KeyError, TypeError):
            return False