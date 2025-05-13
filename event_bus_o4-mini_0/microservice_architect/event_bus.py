import threading
import time
import uuid
from contextlib import contextmanager

class EventBus:
    def __init__(self):
        self._subscribers = {}  # handle -> {"handler", "once", "error_callback"}
        self._next_handle = 1
        self._global_error_handler = None
        self._dead_letters = {}  # channel_name -> list of (event, exception)
        # filters now store tuples of (predicate_fn, threshold_handle)
        self._filters = []
        self._logger = None
        self._in_transaction = False
        self._transaction_buffer = []
        self._context_middleware_enabled = False
        self._thread_local = threading.local()

    def subscribe(self, handler):
        handle = self._next_handle
        self._next_handle += 1
        self._subscribers[handle] = {
            "handler": handler,
            "once": False,
            "error_callback": None
        }
        if self._logger:
            self._logger.on_subscribe(handler)
        return handle

    def subscribe_once(self, handler):
        handle = self._next_handle
        self._next_handle += 1
        self._subscribers[handle] = {
            "handler": handler,
            "once": True,
            "error_callback": None
        }
        if self._logger:
            self._logger.on_subscribe(handler)
        return handle

    def unsubscribe(self, handle):
        sub = self._subscribers.pop(handle, None)
        if sub and self._logger:
            self._logger.on_unsubscribe(sub["handler"])

    def set_global_error_handler(self, fn):
        self._global_error_handler = fn

    def on_error(self, handler, error_callback):
        # attach error_callback to all subscriptions matching handler
        for sub in self._subscribers.values():
            if sub["handler"] == handler:
                sub["error_callback"] = error_callback

    def dead_letter_queue(self, channel_name):
        self._dead_letters[channel_name] = []
        return self._dead_letters[channel_name]

    def add_filter(self, predicate_fn):
        # record a filter that applies to all subscribers existing up to now
        # threshold is the max handle assigned so far
        threshold = self._next_handle - 1
        self._filters.append((predicate_fn, threshold))

    def attach_logger(self, logger):
        self._logger = logger

    def context_middleware(self):
        self._context_middleware_enabled = True

    def set_context(self, key, value):
        if not hasattr(self._thread_local, "context"):
            self._thread_local.context = {}
        self._thread_local.context[key] = value

    def get_context(self, key, default=None):
        return getattr(self._thread_local, "context", {}).get(key, default)

    def publish(self, event):
        if self._in_transaction:
            self._transaction_buffer.append(event)
        else:
            self._dispatch(event)

    def _dispatch(self, event):
        # Determine which subscribers should receive the event based on filters
        recipients = []
        try:
            for handle, sub in list(self._subscribers.items()):
                # Check each filter: only apply filters whose threshold >= this handle
                skip = False
                for pred, threshold in self._filters:
                    if handle <= threshold:
                        # this subscriber is subject to this filter
                        try:
                            if not pred(event):
                                skip = True
                                break
                        except Exception as fe:
                            # filter error: global error handler, then abort dispatch
                            if self._global_error_handler:
                                self._global_error_handler(fe, event)
                            return
                if not skip:
                    recipients.append((handle, sub))
        except Exception:
            # safety net (though filter errors handled above)
            return

        if not recipients:
            # nothing to deliver: drop
            if self._logger:
                self._logger.on_filter_drop(event)
            return

        # Publish hook after passing filters
        if self._logger:
            self._logger.on_publish(event)

        # Deliver to subscribers
        to_unsubscribe = []
        for handle, sub in recipients:
            handler = sub["handler"]
            try:
                if self._context_middleware_enabled:
                    # context is already assumed to be set via set_context
                    pass
                handler(event)
                if self._logger:
                    self._logger.on_deliver(handler, event)
            except Exception as e:
                # subscriber-level error handler
                if sub["error_callback"]:
                    try:
                        sub["error_callback"](e, event)
                    except Exception as e2:
                        if self._global_error_handler:
                            self._global_error_handler(e2, event)
                elif self._global_error_handler:
                    self._global_error_handler(e, event)
                # route to dead-letter queues
                for queue in self._dead_letters.values():
                    queue.append((event, e))
                if self._logger:
                    self._logger.on_error(handler, event, e)
            if sub["once"]:
                to_unsubscribe.append(handle)

        for handle in to_unsubscribe:
            self.unsubscribe(handle)

    def publish_delayed(self, event, delay_secs):
        timer = threading.Timer(delay_secs, lambda: self.publish(event))
        timer.daemon = True
        timer.start()
        return timer

    @contextmanager
    def with_transaction(self):
        already_in_tx = self._in_transaction
        if not already_in_tx:
            self._in_transaction = True
            self._transaction_buffer = []
        try:
            yield
            if not already_in_tx:
                # commit
                for ev in self._transaction_buffer:
                    self._dispatch(ev)
        except:
            # rollback on error
            if not already_in_tx:
                self._transaction_buffer = []
            raise
        finally:
            if not already_in_tx:
                self._in_transaction = False
                self._transaction_buffer = []
