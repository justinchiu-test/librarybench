"""
Microservice Owner EventBus implementation for testing
"""
import threading
import time
from concurrent.futures import ThreadPoolExecutor


class EventBus:
    def __init__(self):
        # Serializer registry: name -> (encode_fn, decode_fn)
        self._serializers = {}
        # Handlers per topic: topic -> [func]
        self._handlers = {}
        # Executor for async publish
        self._executor = ThreadPoolExecutor()
        # Context storage
        class _Ctx: pass
        self.context = _Ctx()
        # Persistence flags and store
        self.persistent_enabled = False
        self.replay_mode = False
        self.persistent_store = []
        # Extensions
        self._extensions = []
        # Configuration
        self.config = {}
        # Authentication tokens per topic
        self._auth = {}
        # Poison queue for failed events
        self.poison_queue = []
        # Default max retries for handler errors
        self.max_retries = 3
        # Round-robin indices
        self._rr_indices = {}
        self._wr_indices = {}

    def registerSerializer(self, name, encode_fn, decode_fn):
        self._serializers[name] = (encode_fn, decode_fn)

    def serialize(self, name, data):
        if name not in self._serializers:
            raise KeyError(f"Serializer '{name}' not found")
        enc, _ = self._serializers[name]
        return enc(data)

    def deserialize(self, name, blob):
        if name not in self._serializers:
            raise KeyError(f"Serializer '{name}' not found")
        _, dec = self._serializers[name]
        return dec(blob)

    def propagateContext(self, context, func, *args, **kwargs):
        # Set context for duration of func
        old = getattr(self.context, 'data', None)
        self.context.data = context
        try:
            return func(*args, **kwargs)
        finally:
            if old is None:
                delattr(self.context, 'data')
            else:
                self.context.data = old

    def registerHandler(self, topic, handler):
        self._handlers.setdefault(topic, []).append(handler)

    def persistEvents(self, enabled, replay_mode=False):
        self.persistent_enabled = enabled
        self.replay_mode = replay_mode
    
    def authenticate(self, topic, token):
        """Register a valid token for a topic"""
        self._auth.setdefault(topic, set()).add(token)

    def publishSync(self, topic, event, async_=False, token=None):
        # Authorization: if topic has auth mapping, require valid token
        if topic in self._auth and token not in self._auth.get(topic, set()):
            raise PermissionError(f"Unauthorized for topic '{topic}'")
        # Persist if enabled
        if self.persistent_enabled:
            self.persistent_store.append((topic, event, None))

        # Handler invocation with retries and poison on failure
        def _invoke():
            for h in self._handlers.get(topic, []):
                error_occurred = False
                # attempt handler up to max_retries
                for _ in range(self.max_retries):
                    try:
                        h(event)
                        break
                    except Exception:
                        error_occurred = True
                        continue
                # if any error occurred during attempts, poison the event
                if error_occurred:
                    self.poison_queue.append((topic, event))
            # call extensions
            for ext in self._extensions:
                ext(topic, event)

        if async_:
            self._executor.submit(_invoke)
        else:
            _invoke()

    publish = publishSync

    def replay(self):
        # Replay only if both flags set
        if not (self.persistent_enabled and self.replay_mode):
            return
        for topic, event, _ in list(self.persistent_store):
            # replay synchronously
            for h in self._handlers.get(topic, []):
                self._executor.submit(h, event)

    def reportHealth(self):
        return {
            'thread_pool_max_workers': getattr(self._executor, '_max_workers', None),
            'queue_size': 0,
            'handler_counts': {topic: len(hs) for topic, hs in self._handlers.items()}
        }

    def balanceLoad(self, key, reps, weights=None):
        if weights is None:
            idx = self._rr_indices.get(key, 0)
            pick = reps[idx % len(reps)]
            self._rr_indices[key] = idx + 1
            return pick
        # weighted round robin
        weighted = []
        for r, w in zip(reps, weights):
            weighted.extend([r] * w)
        idx = self._wr_indices.get(key, 0)
        pick = weighted[idx % len(weighted)]
        self._wr_indices[key] = idx + 1
        return pick

    def updateConfig(self, **kwargs):
        for k, v in kwargs.items():
            self.config[k] = v

    def registerExtension(self, ext):
        self._extensions.append(ext)