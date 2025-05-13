import threading
import uuid
import time
from contextlib import contextmanager
import contextvars

_event_context = contextvars.ContextVar('event_context', default={})

class EventBus:
    def __init__(self):
        self._subscriptions = {}  # handle -> (handler, once)
        self._filters = []
        self._error_handlers = {}  # handler -> error_callback
        self._global_error_handler = None
        self._dead_letter_queue = None
        self._logger = None
        self._in_transaction = False
        self._transaction_buffer = []

    def subscribe(self, handler):
        handle = uuid.uuid4().hex
        self._subscriptions[handle] = (handler, False)
        if self._logger:
            self._logger.log_subscribe(handle, handler)
        return handle

    def subscribe_once(self, handler):
        handle = uuid.uuid4().hex
        self._subscriptions[handle] = (handler, True)
        if self._logger:
            self._logger.log_subscribe(handle, handler, once=True)
        return handle

    def unsubscribe(self, handle):
        if handle in self._subscriptions:
            handler = self._subscriptions[handle][0]
            del self._subscriptions[handle]
            if self._logger:
                self._logger.log_unsubscribe(handle, handler)

    def set_global_error_handler(self, fn):
        self._global_error_handler = fn

    def on_error(self, handler, error_callback):
        self._error_handlers[handler] = error_callback

    def dead_letter_queue(self, queue_event_type):
        self._dead_letter_queue = queue_event_type

    def add_filter(self, filter_fn):
        self._filters.append(filter_fn)

    def attach_logger(self, logger):
        self._logger = logger

    def publish(self, event_type, payload=None):
        event = {'type': event_type, 'payload': payload, 'context': _event_context.get()}
        if self._logger:
            self._logger.log_publish(event)
        # Apply filters
        for f in self._filters:
            try:
                if not f(event):
                    return
            except Exception as fe:
                # filter error, skip delivery
                if self._logger:
                    self._logger.log_error(f, event, fe)
                return
        if self._in_transaction:
            # buffer the event (store the actual event dict for commit)
            self._transaction_buffer.append((event_type, payload, event))
        else:
            self._deliver(event)

    def _deliver(self, event):
        to_remove = []
        for handle, (handler, once) in list(self._subscriptions.items()):
            try:
                handler(event)
                if self._logger:
                    self._logger.log_delivery(handler, event)
            except Exception as e:
                # handler-specific error callback
                cb = self._error_handlers.get(handler)
                if cb:
                    try:
                        cb(event, e)
                    except Exception:
                        pass
                # global error handler
                if self._global_error_handler:
                    try:
                        self._global_error_handler(event, e)
                    except Exception:
                        pass
                # republish to dead letter queue, but avoid infinite loop
                if self._dead_letter_queue and event.get('type') != self._dead_letter_queue:
                    try:
                        self.publish(self._dead_letter_queue, {'original': event, 'error': str(e)})
                    except Exception:
                        pass
                if self._logger:
                    self._logger.log_error(handler, event, e)
            if once:
                to_remove.append(handle)
        for handle in to_remove:
            self.unsubscribe(handle)

    def publish_delayed(self, event_type, payload, delay_secs):
        def target():
            self.publish(event_type, payload)
        t = threading.Timer(delay_secs, target)
        t.daemon = True
        t.start()
        return t

    @contextmanager
    def with_transaction(self):
        prev_in_tx = self._in_transaction
        prev_buffer = self._transaction_buffer
        # start new transaction
        self._in_transaction = True
        self._transaction_buffer = []
        try:
            yield
        except Exception:
            # rollback: discard buffered events
            self._transaction_buffer = []
            # restore flags and re-raise
            raise
        else:
            # commit buffered events
            for _etype, _payload, ev in self._transaction_buffer:
                self._deliver(ev)
        finally:
            # restore previous state
            self._in_transaction = prev_in_tx
            self._transaction_buffer = prev_buffer

    @contextmanager
    def context_middleware(self, **ctx):
        token = _event_context.set({**_event_context.get(), **ctx})
        try:
            yield
        finally:
            _event_context.reset(token)
