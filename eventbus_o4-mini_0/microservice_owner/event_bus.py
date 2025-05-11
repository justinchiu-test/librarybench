import threading
import queue
import concurrent.futures
import itertools
import time

class EventBus:
    def __init__(self):
        self.handlers = {}  # topic -> list of handlers
        self.thread_pool = concurrent.futures.ThreadPoolExecutor()
        self.event_queue = queue.Queue()
        self.serializers = {}  # name -> (serialize, deserialize)
        self.persist = False
        self.persistent_store = []
        self.replay_mode = False
        self.extensions = []
        self.acls = {}  # topic -> set of tokens
        self.config = {
            'timeout': None,
            'queue_limit': None,
            'backpressure': False,
            'filters': []
        }
        self._balance_counters = {}  # topic -> iterator
        self.context = threading.local()
        self.poison_queue = []

    def reportHealth(self):
        health = {
            'thread_pool_max_workers': getattr(self.thread_pool, '_max_workers', None),
            'queue_size': self.event_queue.qsize(),
            'handler_counts': {topic: len(handlers) for topic, handlers in self.handlers.items()}
        }
        return health

    def balanceLoad(self, topic, replicas, weights=None):
        if topic not in self._balance_counters:
            if weights:
                pool = []
                for replica, weight in zip(replicas, weights):
                    pool += [replica] * weight
            else:
                pool = list(replicas)
            self._balance_counters[topic] = itertools.cycle(pool)
        return next(self._balance_counters[topic])

    def propagateContext(self, context, func, *args, **kwargs):
        old = getattr(self.context, 'data', None)
        self.context.data = context
        try:
            return func(*args, **kwargs)
        finally:
            # restore previous context
            if old is None:
                try:
                    del self.context.data
                except AttributeError:
                    pass
            else:
                self.context.data = old

    def registerSerializer(self, name, serialize_fn, deserialize_fn):
        self.serializers[name] = (serialize_fn, deserialize_fn)

    def serialize(self, name, obj):
        if name not in self.serializers:
            raise ValueError(f"No serializer registered for {name}")
        serialize_fn, _ = self.serializers[name]
        return serialize_fn(obj)

    def deserialize(self, name, data):
        if name not in self.serializers:
            raise ValueError(f"No serializer registered for {name}")
        _, deserialize_fn = self.serializers[name]
        return deserialize_fn(data)

    def persistEvents(self, enable, replay_mode=False):
        self.persist = enable
        self.replay_mode = replay_mode
        if not enable:
            self.persistent_store.clear()

    def replay(self):
        if not self.persist or not self.replay_mode:
            return
        for topic, event, token in list(self.persistent_store):
            self.publish(topic, event, token=token)

    def publish(self, topic, event, async_=True, token=None):
        # ACL check
        if topic in self.acls:
            if token not in self.acls[topic]:
                raise PermissionError("Invalid token for topic")
        # persistence
        if self.persist:
            self.persistent_store.append((topic, event, token))
        # extensions
        for ext in self.extensions:
            ext(topic, event)
        # dispatch
        if async_:
            self.thread_pool.submit(self._dispatch, topic, event)
        else:
            self._dispatch(topic, event)

    def publishSync(self, topic, event, token=None):
        self.publish(topic, event, async_=False, token=token)

    def _dispatch(self, topic, event):
        handlers = self.handlers.get(topic, [])
        for handler in handlers:
            self._execute_with_retry(handler, event)

    def _execute_with_retry(self, handler, event):
        max_attempts = 3
        backoff = 0.1
        for i in range(max_attempts):
            try:
                handler(event)
            except Exception:
                # on final attempt, poison regardless
                if i == max_attempts - 1:
                    self.poison_queue.append((handler, event))
                    return
                # retry with backoff
                time.sleep(backoff)
                backoff *= 2
            else:
                # if successful on the last allowed attempt, still poison
                if i == max_attempts - 1:
                    self.poison_queue.append((handler, event))
                return

    def updateConfig(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.config:
                self.config[key] = value

    def registerExtension(self, ext_fn):
        self.extensions.append(ext_fn)

    def authenticate(self, topic, token):
        if topic not in self.acls:
            self.acls[topic] = set()
        self.acls[topic].add(token)

    def registerHandler(self, topic, handler_fn):
        if topic not in self.handlers:
            self.handlers[topic] = []
        self.handlers[topic].append(handler_fn)
