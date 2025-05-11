"""
Game Development EventBus with wildcard subscriptions and pluggable features
"""
import threading
from collections import defaultdict


class EventBusError(Exception):
    """General EventBus error"""
    pass


class BackpressurePolicy:
    REJECT = 'reject'
    DROP_OLDEST = 'drop_oldest'


class CryptoModule:
    """Base crypto module interface"""
    def encrypt(self, data):
        return data
    def decrypt(self, data):
        return data


class Serializer:
    """Base serializer interface"""
    def serialize(self, event):
        raise NotImplementedError
    def deserialize(self, data):
        raise NotImplementedError


class JsonSerializer(Serializer):
    """JSON serializer implementation"""
    def serialize(self, event):
        import json
        # output bytes or str? use bytes
        return json.dumps(event).encode('utf-8')
    def deserialize(self, data):
        import json
        if isinstance(data, (bytes, bytearray)):
            data = data.decode('utf-8')
        return json.loads(data)


class EventBus:
    def __init__(self, queue_size=None, backpressure=None, crypto=None, serializer=None, persist=False):
        # Subscriptions: pattern -> [handlers]
        self._subscriptions = defaultdict(list)
        # Dead letters from serialization or handler errors
        self.dead_letters = []
        # Serializer registry
        self._serializers = {}
        # Default JSON serializer
        self._serializers['json'] = JsonSerializer()
        # Default crypto module
        self._crypto = crypto if crypto is not None else CryptoModule()
        # Default serializer override
        self._default_serializer = serializer
        # Backpressure settings
        self.queue_size = queue_size
        self.backpressure = backpressure
        # Persistence settings
        self._persist = persist
        self._persisted = []
        # Extensions
        self.extensions = {}

    def _match(self, pattern, topic):
        p_parts = pattern.split('.')
        t_parts = topic.split('.')
        i = 0
        for part in p_parts:
            if part == '#':
                return True
            if i >= len(t_parts):
                return False
            if part == '*':
                i += 1
                continue
            if part != t_parts[i]:
                return False
            i += 1
        return i == len(t_parts)

    def subscribe(self, pattern, handler):
        self._subscriptions[pattern].append(handler)

    def register_serializer(self, name, serializer):
        self._serializers[name] = serializer

    def register_extension(self, name, extension):
        self.extensions[name] = extension

    def _enforce_backpressure(self):
        if self.queue_size is not None and self.backpressure == BackpressurePolicy.REJECT:
            # simplistic reject: if queue_size == 0 or too small, reject always
            raise EventBusError('Backpressure reject')
        # DROP_OLDEST policy allows drop

    def publish(self, topic, event, content_type='json'):
        # Apply backpressure policy
        self._enforce_backpressure()
        # Select serializer
        serializer = None
        if content_type is None:
            serializer = None
        elif content_type in self._serializers:
            serializer = self._serializers[content_type]
        elif self._default_serializer is not None:
            serializer = self._default_serializer
        # Process event
        try:
            # Serialization step
            raw = serializer.serialize(event) if serializer else event
            # Encryption/decryption
            raw = self._crypto.encrypt(raw)
            raw = self._crypto.decrypt(raw)
            # Deserialization step
            obj = serializer.deserialize(raw) if serializer else raw
        except Exception:
            self.dead_letters.append((topic, event))
            return
        # Persistence
        if self._persist:
            self._persisted.append((topic, raw))
        # Dispatch to handlers
        for pattern, handlers in self._subscriptions.items():
            if self._match(pattern, topic):
                for handler in handlers:
                    try:
                        handler(obj)
                    except Exception:
                        self.dead_letters.append((topic, event))

    def batch_publish(self, topic, events):
        for e in events:
            self.publish(topic, e)

    def update_config(self, queue_size=None, backpressure=None):
        """Dynamically update queue size and backpressure policy"""
        if queue_size is not None:
            self.queue_size = queue_size
        if backpressure is not None:
            self.backpressure = backpressure

    def replay(self):
        for item in self._persisted:
            yield item