class HandlerRegistry:
    """Registry for event handlers filtered by event type and path prefix."""
    def __init__(self):
        self._handlers = []  # list of tuples (event_type, path_prefix, handler)

    def register(self, event_type: str, path_prefix: str, handler):
        """Register a handler for a given event_type and path_prefix."""
        self._handlers.append((event_type, path_prefix, handler))

    def dispatch(self, event):
        """Dispatch an event to matching handlers."""
        for etype, prefix, handler in self._handlers:
            if event.event_type == etype and event.src_path.startswith(prefix):
                handler(event)
