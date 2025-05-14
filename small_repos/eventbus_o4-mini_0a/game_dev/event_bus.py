import threading
import time
import json
from enum import Enum

class EventBusError(Exception):
    pass

class BackpressurePolicy(Enum):
    BLOCK = "block"
    DROP_OLDEST = "drop_oldest"
    REJECT = "reject"

class CryptoModule:
    def encrypt(self, data: bytes) -> bytes:
        raise NotImplementedError

    def decrypt(self, data: bytes) -> bytes:
        raise NotImplementedError

class DefaultCrypto(CryptoModule):
    def encrypt(self, data: bytes) -> bytes:
        return data

    def decrypt(self, data: bytes) -> bytes:
        return data

class Serializer:
    def serialize(self, event) -> bytes:
        raise NotImplementedError

    def deserialize(self, data: bytes):
        raise NotImplementedError

class JsonSerializer(Serializer):
    def serialize(self, event) -> bytes:
        return json.dumps(event).encode('utf-8')

    def deserialize(self, data: bytes):
        return json.loads(data.decode('utf-8'))

class EventBus:
    def __init__(
        self,
        queue_size: int = 100,
        backpressure: BackpressurePolicy = BackpressurePolicy.REJECT,
        crypto: CryptoModule = None,
        serializer: Serializer = None,
        persist: bool = False,
    ):
        self.subscriptions = []  # list of (pattern, handler)
        self.dead_letters = []  # list of (topic, raw_event)
        self._queue = []  # internal pending queue
        self.queue_size = queue_size
        self.backpressure = backpressure
        self.crypto = crypto or DefaultCrypto()
        self.default_serializer = serializer or JsonSerializer()
        self.serializers = {}  # content_type -> Serializer
        self.persist = persist
        self.persisted_events = []
        self.extensions = {}
        self._lock = threading.Lock()

    def subscribe(self, pattern: str, handler):
        self.subscriptions.append((pattern, handler))

    def register_serializer(self, content_type: str, serializer: Serializer):
        self.serializers[content_type] = serializer

    def register_extension(self, name: str, extension):
        self.extensions[name] = extension

    def update_config(
        self,
        queue_size: int = None,
        backpressure: BackpressurePolicy = None,
    ):
        if queue_size is not None:
            self.queue_size = queue_size
        if backpressure is not None:
            self.backpressure = backpressure

    def _match(self, topic: str, pattern: str) -> bool:
        """
        Match a topic against a pattern using single-level (*) and multi-level (#) wildcards.
        '*' matches exactly one token; '#' matches zero or more tokens.
        """
        t_tokens = topic.split('.')
        p_tokens = pattern.split('.')
        t_i = 0
        p_i = 0
        while p_i < len(p_tokens):
            p_tok = p_tokens[p_i]
            if p_tok == '#':
                # Multi-level wildcard consumes the rest (including zero tokens)
                return True
            if t_i >= len(t_tokens):
                # No more topic tokens to match
                return False
            if p_tok == '*':
                # Single-level wildcard matches exactly one token
                t_i += 1
                p_i += 1
            else:
                # Literal match
                if p_tok != t_tokens[t_i]:
                    return False
                t_i += 1
                p_i += 1
        # After processing pattern, topic must also be fully matched
        return t_i == len(t_tokens)

    def publish(self, topic: str, event, content_type: str = None):
        serializer = self.serializers.get(content_type, self.default_serializer)
        try:
            raw = serializer.serialize(event)
        except Exception:
            # Malformed event goes to dead letter
            self.dead_letters.append((topic, event))
            return
        # Backpressure check
        with self._lock:
            if len(self._queue) >= self.queue_size:
                if self.backpressure == BackpressurePolicy.REJECT:
                    raise EventBusError("Backpressure: queue full")
                elif self.backpressure == BackpressurePolicy.DROP_OLDEST:
                    if self._queue:
                        self._queue.pop(0)
                elif self.backpressure == BackpressurePolicy.BLOCK:
                    while len(self._queue) >= self.queue_size:
                        time.sleep(0.01)
            self._queue.append((topic, raw, serializer))
        # Persist if enabled
        if self.persist:
            self.persisted_events.append((topic, raw))
        # Encrypt
        encrypted = self.crypto.encrypt(raw)
        # Deliver and remove from queue
        with self._lock:
            try:
                self._queue.remove((topic, raw, serializer))
            except ValueError:
                pass
        for pattern, handler in list(self.subscriptions):
            if self._match(topic, pattern):
                try:
                    decrypted = self.crypto.decrypt(encrypted)
                    msg = serializer.deserialize(decrypted)
                    handler(msg)
                except Exception:
                    self.dead_letters.append((topic, event))

    def batch_publish(self, topic: str, events, content_type: str = None):
        for ev in events:
            self.publish(topic, ev, content_type=content_type)

    def replay(self):
        for topic, raw in self.persisted_events:
            yield topic, raw
