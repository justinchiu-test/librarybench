import threading
import uuid

class EventBus:
    def __init__(self):
        self.subscriptions = {}  # id: dict(handler, once)
        self.error_callbacks = {}  # handler->callback
        self.global_error_handler = None
        self.filters = []
        self.middleware = []
        self.logger = None
        self.dlq_name = None
        self.dead_letters = {}  # name->list
        self._tx_buffer = None
        self._lock = threading.Lock()

    def attach_logger(self, logger):
        self.logger = logger
        if self.logger:
            self.logger.info("Logger attached")

    def add_filter(self, filter_fn):
        self.filters.append(filter_fn)
        if self.logger:
            self.logger.info(f"Filter added: {filter_fn}")

    def context_middleware(self):
        def middleware_fn(event):
            event['_context'] = {
                'device_id': event.get('device_id'),
                'firmware': event.get('firmware'),
                'trace': event.get('trace', str(uuid.uuid4()))
            }
            return event
        self.middleware.append(middleware_fn)
        if self.logger:
            self.logger.info("Context middleware added")

    def dead_letter_queue(self, name):
        self.dlq_name = name
        self.dead_letters[name] = []
        if self.logger:
            self.logger.info(f"Dead letter queue created: {name}")

    def set_global_error_handler(self, fn):
        self.global_error_handler = fn
        if self.logger:
            self.logger.info("Global error handler set")

    def on_error(self, handler, error_callback):
        self.error_callbacks[handler] = error_callback
        if self.logger:
            self.logger.info(f"Error callback set for handler {handler}")

    def subscribe(self, handler):
        sub_id = str(uuid.uuid4())
        self.subscriptions[sub_id] = {'handler': handler, 'once': False}
        if self.logger:
            self.logger.info(f"Subscribed handler {handler} with id {sub_id}")
        return sub_id

    def subscribe_once(self, handler):
        sub_id = str(uuid.uuid4())
        self.subscriptions[sub_id] = {'handler': handler, 'once': True}
        if self.logger:
            self.logger.info(f"Subscribed once handler {handler} with id {sub_id}")
        return sub_id

    def unsubscribe(self, sub_id):
        if sub_id in self.subscriptions:
            handler = self.subscriptions[sub_id]['handler']
            del self.subscriptions[sub_id]
            if self.logger:
                self.logger.info(f"Unsubscribed handler {handler} with id {sub_id}")

    def publish(self, event):
        # Buffer if in transaction
        if self._tx_buffer is not None:
            self._tx_buffer.append(('publish', (event,), {}))
            if self.logger:
                self.logger.info(f"Buffered event {event} in transaction")
            return
        # apply filters
        for f in self.filters:
            try:
                if not f(event):
                    if self.logger:
                        self.logger.info(f"Event {event} dropped by filter {f}")
                    return
            except Exception as exc:
                if self.dlq_name:
                    self.dead_letters[self.dlq_name].append(event)
                if self.logger:
                    self.logger.error(f"Filter error {exc} on event {event}")
                return
        # apply middleware
        for m in self.middleware:
            try:
                event = m(event)
            except Exception as exc:
                if self.dlq_name:
                    self.dead_letters[self.dlq_name].append(event)
                if self.logger:
                    self.logger.error(f"Middleware error {exc} on event {event}")
                return
        # dispatch
        to_remove = []
        for sub_id, info in list(self.subscriptions.items()):
            handler = info['handler']
            try:
                if self.logger:
                    self.logger.info(f"Publishing event {event} to handler {handler}")
                handler(event)
                if self.logger:
                    self.logger.info(f"Delivered event {event} to handler {handler}")
                if info['once']:
                    to_remove.append(sub_id)
            except Exception as exc:
                cb = self.error_callbacks.get(handler)
                if cb:
                    try:
                        cb(event, exc)
                    except Exception:
                        pass
                if self.global_error_handler:
                    try:
                        self.global_error_handler(exc, event)
                    except Exception:
                        pass
                if self.dlq_name:
                    self.dead_letters[self.dlq_name].append((event, exc))
                if self.logger:
                    self.logger.error(f"Error {exc} in handler {handler} for event {event}")
                if info['once']:
                    to_remove.append(sub_id)
        for sub_id in to_remove:
            self.unsubscribe(sub_id)

    def publish_delayed(self, event, delay_secs):
        if self._tx_buffer is not None:
            self._tx_buffer.append(('_delayed', (event, delay_secs), {}))
            if self.logger:
                self.logger.info(f"Buffered delayed event {event} in transaction")
        else:
            timer = threading.Timer(delay_secs, lambda: self.publish(event))
            timer.daemon = True
            timer.start()
            if self.logger:
                self.logger.info(f"Scheduled delayed event {event} after {delay_secs}s")

    def _delayed(self, event, delay_secs):
        timer = threading.Timer(delay_secs, lambda: self.publish(event))
        timer.daemon = True
        timer.start()

    def with_transaction(self):
        return Transaction(self)

class Transaction:
    def __init__(self, bus):
        self.bus = bus

    def __enter__(self):
        self.bus._tx_buffer = []
        if self.bus.logger:
            self.bus.logger.info("Transaction started")
        return self

    def __exit__(self, exc_type, exc, tb):
        buffer = self.bus._tx_buffer
        self.bus._tx_buffer = None
        if exc:
            if self.bus.logger:
                self.bus.logger.info("Transaction aborted due to exception")
            return False
        if self.bus.logger:
            self.bus.logger.info("Transaction committing")
        for method, args, kwargs in buffer:
            if method == '_delayed':
                self.bus._delayed(*args, **kwargs)
            elif method == 'publish':
                self.bus.publish(*args, **kwargs)
        return False

# Singleton instance
bus = EventBus()
