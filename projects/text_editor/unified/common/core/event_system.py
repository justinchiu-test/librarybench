"""
Event system module for managing events and subscriptions.

This module provides an event management system that allows components
to subscribe to and publish events, enabling loose coupling between
different parts of the text editor.
"""

from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of events that can be published in the system."""

    # Content events
    CONTENT_CHANGED = "content_changed"
    CONTENT_INSERTED = "content_inserted"
    CONTENT_DELETED = "content_deleted"
    CONTENT_REPLACED = "content_replaced"

    # File events
    FILE_OPENED = "file_opened"
    FILE_SAVED = "file_saved"
    FILE_CLOSED = "file_closed"

    # Position events
    POSITION_CHANGED = "position_changed"

    # History events
    HISTORY_UPDATED = "history_updated"
    OPERATION_UNDONE = "operation_undone"
    OPERATION_REDONE = "operation_redone"

    # View events
    VIEW_UPDATED = "view_updated"
    VIEW_SCROLLED = "view_scrolled"

    # Selection events
    SELECTION_CHANGED = "selection_changed"

    # Custom events
    CUSTOM = "custom"


class EventData(BaseModel):
    """Base class for event data."""

    event_type: EventType
    timestamp: float = Field(default_factory=lambda: __import__("time").time())
    source: Optional[str] = None

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True


class ContentEventData(EventData):
    """Event data for content-related events."""

    position: Optional[dict] = None
    text: Optional[str] = None
    start_position: Optional[dict] = None
    end_position: Optional[dict] = None


class FileEventData(EventData):
    """Event data for file-related events."""

    file_path: str
    file_size: Optional[int] = None
    encoding: Optional[str] = None


class PositionEventData(EventData):
    """Event data for position-related events."""

    old_position: dict
    new_position: dict


class HistoryEventData(EventData):
    """Event data for history-related events."""

    operation: dict


class ViewEventData(EventData):
    """Event data for view-related events."""

    view_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SelectionEventData(EventData):
    """Event data for selection-related events."""

    start_position: dict
    end_position: dict


class CustomEventData(EventData):
    """Event data for custom events."""

    name: str
    data: Dict[str, Any] = Field(default_factory=dict)


EventHandler = Callable[[EventData], None]


class EventSystem:
    """
    Event management system for text editors.

    This class provides functionality for subscribing to and publishing events,
    enabling components to communicate without direct dependencies.
    """

    def __init__(self):
        """Initialize a new event system."""
        self._subscribers: Dict[EventType, List[EventHandler]] = {}
        for event_type in EventType:
            self._subscribers[event_type] = []

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: The type of event to subscribe to
            handler: The function to call when the event is published
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> bool:
        """
        Unsubscribe from an event type.

        Args:
            event_type: The type of event to unsubscribe from
            handler: The handler function to remove

        Returns:
            True if the handler was removed, False otherwise
        """
        if event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
            return True
        return False

    def publish(self, event_data: EventData) -> None:
        """
        Publish an event.

        Args:
            event_data: The event data to publish
        """
        if event_data.event_type not in self._subscribers:
            return

        for handler in self._subscribers[event_data.event_type]:
            try:
                handler(event_data)
            except Exception as e:
                # In a real system, this would be logged
                print(f"Error in event handler: {e}")

    def publish_content_changed(self, source: Optional[str] = None, **kwargs) -> None:
        """
        Publish a content changed event.

        Args:
            source: The source of the event
            **kwargs: Additional data for the event
        """
        event_data = ContentEventData(
            event_type=EventType.CONTENT_CHANGED, source=source, **kwargs
        )
        self.publish(event_data)

    def publish_file_opened(
        self,
        file_path: str,
        file_size: Optional[int] = None,
        encoding: Optional[str] = None,
        source: Optional[str] = None,
    ) -> None:
        """
        Publish a file opened event.

        Args:
            file_path: The path of the opened file
            file_size: The size of the opened file
            encoding: The encoding of the opened file
            source: The source of the event
        """
        event_data = FileEventData(
            event_type=EventType.FILE_OPENED,
            file_path=file_path,
            file_size=file_size,
            encoding=encoding,
            source=source,
        )
        self.publish(event_data)

    def publish_position_changed(
        self, old_position: dict, new_position: dict, source: Optional[str] = None
    ) -> None:
        """
        Publish a position changed event.

        Args:
            old_position: The old position
            new_position: The new position
            source: The source of the event
        """
        event_data = PositionEventData(
            event_type=EventType.POSITION_CHANGED,
            old_position=old_position,
            new_position=new_position,
            source=source,
        )
        self.publish(event_data)

    def publish_custom_event(
        self, name: str, data: Dict[str, Any], source: Optional[str] = None
    ) -> None:
        """
        Publish a custom event.

        Args:
            name: The name of the custom event
            data: The data for the custom event
            source: The source of the event
        """
        event_data = CustomEventData(
            event_type=EventType.CUSTOM, name=name, data=data, source=source
        )
        self.publish(event_data)
