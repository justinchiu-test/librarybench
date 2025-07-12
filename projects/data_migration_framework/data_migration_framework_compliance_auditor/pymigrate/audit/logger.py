"""Cryptographic audit logger implementation."""

import base64
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import pytz
from cryptography.hazmat.primitives import serialization

from pymigrate.audit.crypto import CryptoManager
from pymigrate.audit.storage import AuditStorage
from pymigrate.models import AuditEvent, OperationType


class AuditLogger:
    """Implements cryptographic audit logging with hash chain integrity."""

    def __init__(
        self,
        storage: AuditStorage,
        crypto_manager: Optional[CryptoManager] = None,
        enable_signatures: bool = True,
    ):
        """Initialize the audit logger.

        Args:
            storage: Storage backend for audit logs
            crypto_manager: Cryptographic manager for signing (optional)
            enable_signatures: Whether to sign audit events
        """
        self.storage = storage
        self.crypto_manager = crypto_manager or CryptoManager()
        self.enable_signatures = enable_signatures

        # Generate keys if signing is enabled and no keys are loaded
        if self.enable_signatures:
            if (
                not hasattr(self.crypto_manager, "_private_key")
                or self.crypto_manager._private_key is None
            ):
                self.crypto_manager.generate_key_pair()

    def log_event(
        self,
        actor: str,
        operation: OperationType,
        resource: str,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> AuditEvent:
        """Log an audit event with cryptographic proof.

        Args:
            actor: User or system performing the action
            operation: Type of operation
            resource: Resource being accessed/modified
            details: Additional event details
            timestamp: Event timestamp (defaults to current time)

        Returns:
            The created audit event
        """
        # Generate event ID and timestamp
        event_id = str(uuid.uuid4())
        if timestamp is None:
            timestamp = datetime.now(pytz.UTC)
        elif timestamp.tzinfo is None:
            timestamp = pytz.UTC.localize(timestamp)

        # Get previous event hash for chaining
        latest_event = self.storage.get_latest_event()
        previous_hash = latest_event.hash if latest_event else None

        # Create base event data
        event_data = {
            "event_id": event_id,
            "timestamp": timestamp,
            "actor": actor,
            "operation": operation,
            "resource": resource,
            "details": details or {},
            "previous_hash": previous_hash,
        }

        # Compute hash of event
        event_hash = self.crypto_manager.compute_chain_hash(
            {k: v for k, v in event_data.items() if k != "previous_hash"},
            previous_hash or "",
        )

        # Sign the event if enabled
        signature = None
        if self.enable_signatures:
            signature_data = f"{event_id}|{event_hash}|{timestamp.isoformat()}"
            signature_bytes = self.crypto_manager.sign_data(signature_data.encode())
            signature = base64.b64encode(signature_bytes).decode()

        # Create the audit event
        event = AuditEvent(
            event_id=event_id,
            timestamp=timestamp,
            actor=actor,
            operation=operation,
            resource=resource,
            details=details or {},
            previous_hash=previous_hash,
            hash=event_hash,
            signature=signature,
        )

        # Store the event
        self.storage.store_event(event)

        return event

    def verify_event(self, event: AuditEvent) -> bool:
        """Verify the integrity and signature of an audit event.

        Args:
            event: Event to verify

        Returns:
            True if event is valid, False otherwise
        """
        # Verify hash
        expected_hash = self.crypto_manager.compute_chain_hash(
            {
                "event_id": event.event_id,
                "timestamp": event.timestamp,
                "actor": event.actor,
                "operation": event.operation,
                "resource": event.resource,
                "details": event.details,
            },
            event.previous_hash or "",
        )

        if event.hash != expected_hash:
            return False

        # Verify signature if present
        if event.signature and self.enable_signatures:
            signature_data = (
                f"{event.event_id}|{event.hash}|{event.timestamp.isoformat()}"
            )
            signature_bytes = base64.b64decode(event.signature)
            return self.crypto_manager.verify_signature(
                signature_data.encode(), signature_bytes
            )

        return True

    def verify_chain_integrity(self) -> bool:
        """Verify the integrity of the entire audit log chain.

        Returns:
            True if chain is intact, False otherwise
        """
        return self.storage.verify_integrity()

    def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """Retrieve an audit event by ID.

        Args:
            event_id: ID of event to retrieve

        Returns:
            Event if found, None otherwise
        """
        return self.storage.get_event(event_id)

    def get_events_by_timerange(
        self, start_time: datetime, end_time: datetime
    ) -> List[AuditEvent]:
        """Retrieve events within a time range.

        Args:
            start_time: Start of time range
            end_time: End of time range

        Returns:
            List of events in the time range
        """
        return self.storage.get_events_by_timerange(start_time, end_time)

    def get_events_by_actor(self, actor: str) -> List[AuditEvent]:
        """Retrieve all events by a specific actor.

        Args:
            actor: Actor identifier

        Returns:
            List of events by the actor
        """
        return self.storage.get_events_by_actor(actor)

    def get_events_by_resource(self, resource: str) -> List[AuditEvent]:
        """Retrieve all events for a specific resource.

        Args:
            resource: Resource identifier

        Returns:
            List of events for the resource
        """
        return self.storage.get_events_by_resource(resource)

    def export_public_key(self) -> bytes:
        """Export the public key for verification by external parties.

        Returns:
            Public key in PEM format
        """
        if not self.crypto_manager._public_key:
            raise ValueError("No public key available")

        return self.crypto_manager._public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
