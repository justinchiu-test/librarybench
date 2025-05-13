import threading
import uuid
import inspect
from contextlib import contextmanager

class Event:
    def __init__(self, data, context=None):
        self.data = data
        self.context = context or {}

class SubscriptionHandle:
    def __init__(self, id):
        self.id = id

class EventBus:
    def __init__(self):
        self._subscribers = {}           # id -> handler
        self._sub_once = set()           # ids to run once
        self._error_handlers = {}        # handler -> callback
        self._global_error_handler = None
        self.dead_letter_queues = {}     # name -> list
        self._filters = []               # list of filter functions
        self._logger = None
        self._transaction_buffer = None
        self._lock = threading.Lock()

    def attach_logger(self, logger):
        self._logger = logger
        if self._logger:
            self._logger.info("logger_attached")

    def add_filter(self, filter_fn):
        self._filters.append(filter_fn)
        if self._logger:
            self._logger.info("filter_added")

    def set_global_error_handler(self, fn):
        self._global_error_handler = fn
        if self._logger:
            self._logger.info("global_error_handler_set")

    def on_error(self, handler, error_callback):
        self._error_handlers[handler] = error_callback
        if self._logger:
            self._logger.info("error_handler_added")

    def subscribe(self, handler):
        handle = SubscriptionHandle(str(uuid.uuid4()))
        self._subscribers[handle.id] = handler
        if self._logger:
            self._logger.info(f"subscribed:{handler}")
        return handle

    def subscribe_once(self, handler):
        handle = self.subscribe(handler)
        self._sub_once.add(handle.id)
        return handle

    def unsubscribe(self, handle):
        hid = getattr(handle, "id", None)
        if hid in self._subscribers:
            handler = self._subscribers.pop(hid)
            self._sub_once.discard(hid)
            if self._logger:
                self._logger.info(f"unsubscribed:{handler}")

    def dead_letter_queue(self, name):
        q = []
        self.dead_letter_queues[name] = q
        return q

    def publish(self, event_data, context=None):
        event = Event(event_data, context or {})
        # apply filters
        for f in self._filters:
            try:
                if not f(event):
                    if self._logger:
                        self._logger.info("filtered_out")
                    return
            except Exception as e:
                self._handle_error(f, event, e)
                return
        # transaction buffering
        if self._transaction_buffer is not None:
            self._transaction_buffer.append((event, event.context))
            if self._logger:
                self._logger.info("buffered_in_transaction")
            return
        # deliver events
        to_remove = []
        for hid, handler in list(self._subscribers.items()):
            try:
                handler(event)
                if self._logger:
                    self._logger.info(f"delivered:{handler}")
            except Exception as e:
                self._handle_error(handler, event, e)
            if hid in self._sub_once:
                to_remove.append(hid)
        for hid in to_remove:
            self.unsubscribe(SubscriptionHandle(hid))

    def _handle_error(self, handler, event, exception):
        # per-handler error callback
        if handler in self._error_handlers:
            try:
                self._error_handlers[handler](event, exception)
                return
            except Exception as e:
                if self._logger:
                    self._logger.error(f"error_handler_exc:{e}")
        # global error handler
        if self._global_error_handler:
            try:
                self._global_error_handler(event, exception)
                return
            except Exception as e:
                if self._logger:
                    self._logger.error(f"global_error_handler_exc:{e}")

    def publish_delayed(self, event_data, delay_secs):
        timer = threading.Timer(delay_secs, lambda: self.publish(event_data))
        timer.daemon = True
        timer.start()
        if self._logger:
            self._logger.info(f"delayed_publish_scheduled:{delay_secs}")
        return timer

    @contextmanager
    def with_transaction(self):
        old_buffer = self._transaction_buffer
        self._transaction_buffer = []
        if self._logger:
            self._logger.info("transaction_started")
        try:
            yield
            events = self._transaction_buffer
            self._transaction_buffer = old_buffer
            for event, ctx in events:
                self.publish(event.data, event.context)
            if self._logger:
                self._logger.info("transaction_committed")
        except Exception:
            self._transaction_buffer = old_buffer
            if self._logger:
                self._logger.info("transaction_rolled_back")
            raise

    def context_middleware(self):
        def middleware(handler):
            def wrapped(event):
                # set short keys as expected by tests
                event.context.setdefault("corr", str(uuid.uuid4()))
                event.context.setdefault("batch", str(uuid.uuid4()))
                event.context.setdefault("source", inspect.stack()[1].filename)
                handler(event)
            return wrapped
        return middleware
