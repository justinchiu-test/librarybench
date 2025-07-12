"""Storage backends for audit logs."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path

from pymigrate.models import AuditEvent


class AuditStorage(ABC):
    """Abstract base class for audit log storage."""

    @abstractmethod
    def store_event(self, event: AuditEvent) -> None:
        """Store an audit event.

        Args:
            event: Event to store
        """
        pass

    @abstractmethod
    def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """Retrieve an event by ID.

        Args:
            event_id: ID of event to retrieve

        Returns:
            Event if found, None otherwise
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def get_events_by_actor(self, actor: str) -> List[AuditEvent]:
        """Retrieve all events by a specific actor.

        Args:
            actor: Actor identifier

        Returns:
            List of events by the actor
        """
        pass

    @abstractmethod
    def get_events_by_resource(self, resource: str) -> List[AuditEvent]:
        """Retrieve all events for a specific resource.

        Args:
            resource: Resource identifier

        Returns:
            List of events for the resource
        """
        pass

    @abstractmethod
    def get_latest_event(self) -> Optional[AuditEvent]:
        """Get the most recent event.

        Returns:
            Latest event if any exist, None otherwise
        """
        pass

    @abstractmethod
    def verify_integrity(self) -> bool:
        """Verify the integrity of the audit log chain.

        Returns:
            True if integrity is maintained, False otherwise
        """
        pass


class InMemoryAuditStorage(AuditStorage):
    """In-memory storage for audit logs (for testing/development)."""

    def __init__(self):
        """Initialize in-memory storage."""
        self._events: Dict[str, AuditEvent] = {}
        self._event_order: List[str] = []

    def store_event(self, event: AuditEvent) -> None:
        """Store an audit event in memory."""
        self._events[event.event_id] = event
        self._event_order.append(event.event_id)

    def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """Retrieve an event by ID."""
        return self._events.get(event_id)

    def get_events_by_timerange(
        self, start_time: datetime, end_time: datetime
    ) -> List[AuditEvent]:
        """Retrieve events within a time range."""
        return [
            event
            for event in self._events.values()
            if start_time <= event.timestamp <= end_time
        ]

    def get_events_by_actor(self, actor: str) -> List[AuditEvent]:
        """Retrieve all events by a specific actor."""
        return [event for event in self._events.values() if event.actor == actor]

    def get_events_by_resource(self, resource: str) -> List[AuditEvent]:
        """Retrieve all events for a specific resource."""
        return [event for event in self._events.values() if event.resource == resource]

    def get_latest_event(self) -> Optional[AuditEvent]:
        """Get the most recent event."""
        if not self._event_order:
            return None
        return self._events[self._event_order[-1]]

    def verify_integrity(self) -> bool:
        """Verify the integrity of the audit log chain."""
        if not self._event_order:
            return True

        previous_hash = None
        for event_id in self._event_order:
            event = self._events[event_id]
            if event.previous_hash != previous_hash:
                return False
            previous_hash = event.hash

        return True

    def get_all_events(self) -> List[AuditEvent]:
        """Get all events in order."""
        return [self._events[event_id] for event_id in self._event_order]


class FileBasedAuditStorage(AuditStorage):
    """File-based storage for audit logs with append-only semantics."""

    def __init__(self, storage_path: str):
        """Initialize file-based storage.

        Args:
            storage_path: Directory path for storing audit logs
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.log_file = self.storage_path / "audit_log.jsonl"
        self.index_file = self.storage_path / "audit_index.json"
        self._load_index()

    def _load_index(self) -> None:
        """Load the audit log index."""
        if self.index_file.exists():
            with open(self.index_file, "r") as f:
                self._index = json.load(f)
        else:
            self._index = {"events": {}, "latest_event_id": None, "event_count": 0}

    def _save_index(self) -> None:
        """Save the audit log index."""
        with open(self.index_file, "w") as f:
            json.dump(self._index, f, indent=2)

    def store_event(self, event: AuditEvent) -> None:
        """Store an audit event to file."""
        # Append to log file
        with open(self.log_file, "a") as f:
            f.write(event.model_dump_json() + "\n")

        # Update index
        self._index["events"][event.event_id] = {
            "timestamp": event.timestamp.isoformat(),
            "actor": event.actor,
            "resource": event.resource,
            "line_number": self._index["event_count"],
        }
        self._index["latest_event_id"] = event.event_id
        self._index["event_count"] += 1
        self._save_index()

    def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """Retrieve an event by ID."""
        if event_id not in self._index["events"]:
            return None

        line_number = self._index["events"][event_id]["line_number"]
        with open(self.log_file, "r") as f:
            for i, line in enumerate(f):
                if i == line_number:
                    return AuditEvent.model_validate_json(line.strip())
        return None

    def get_events_by_timerange(
        self, start_time: datetime, end_time: datetime
    ) -> List[AuditEvent]:
        """Retrieve events within a time range."""
        events = []
        with open(self.log_file, "r") as f:
            for line in f:
                event = AuditEvent.model_validate_json(line.strip())
                if start_time <= event.timestamp <= end_time:
                    events.append(event)
        return events

    def get_events_by_actor(self, actor: str) -> List[AuditEvent]:
        """Retrieve all events by a specific actor."""
        event_ids = [
            event_id
            for event_id, info in self._index["events"].items()
            if info["actor"] == actor
        ]

        events = []
        for event_id in event_ids:
            event = self.get_event(event_id)
            if event:
                events.append(event)
        return events

    def get_events_by_resource(self, resource: str) -> List[AuditEvent]:
        """Retrieve all events for a specific resource."""
        event_ids = [
            event_id
            for event_id, info in self._index["events"].items()
            if info["resource"] == resource
        ]

        events = []
        for event_id in event_ids:
            event = self.get_event(event_id)
            if event:
                events.append(event)
        return events

    def get_latest_event(self) -> Optional[AuditEvent]:
        """Get the most recent event."""
        if not self._index["latest_event_id"]:
            return None
        return self.get_event(self._index["latest_event_id"])

    def verify_integrity(self) -> bool:
        """Verify the integrity of the audit log chain."""
        if not self.log_file.exists():
            return True

        previous_hash = None
        with open(self.log_file, "r") as f:
            for line in f:
                event = AuditEvent.model_validate_json(line.strip())
                if event.previous_hash != previous_hash:
                    return False
                previous_hash = event.hash

        return True
