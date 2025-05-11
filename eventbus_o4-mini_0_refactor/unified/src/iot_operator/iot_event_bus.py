"""
IoT Operator EventBus with wildcard routing, serialization, encryption, backpressure, and extensions
"""
import json
import os
from collections import deque


class Serializer:
    """Base serializer interface: implement dumps and loads"""
    def dumps(self, obj):
        raise NotImplementedError
    def loads(self, data):
        raise NotImplementedError


class JsonSerializer(Serializer):
    """JSON serializer implementation"""
    def dumps(self, obj):
        # returns bytes
        return json.dumps(obj).encode('utf-8')
    def loads(self, data):
        # data may be bytes
        if isinstance(data, (bytes, bytearray)):
            data = data.decode('utf-8')
        return json.loads(data)


class EventBus:
    def __init__(self):
        # Subscriptions: list of (pattern, handler)
        self._subscriptions = []
        # Dead letters: list of (topic, message)
        self._dead_letters = []
        # Serializer registry: name -> serializer instance
        self._serializers = {}
        # Encryption module
        self._crypto = None
        # Backpressure settings
        self._backpressure_policy = None
        self._queue_limit = None
        # Event queue for backpressure
        self._queue = []
        # Extensions
        self._extensions = []

    def subscribeWildcard(self, pattern, handler):
        """Subscribe to messages matching wildcard pattern using '/' delimiter"""
        self._subscriptions.append((pattern, handler))

    def registerSerializer(self, name, serializer):
        """Register serializer with dumps/loads interface"""
        self._serializers[name] = serializer

    def generateStubs(self):
        """Generate code stubs for each registered serializer"""
        return {name: f"# Stub for serializer '{name}'" for name in self._serializers}

    def encryptEvent(self, crypto):
        """Set encryption/decryption module"""
        self._crypto = crypto

    def applyBackpressure(self, policy, queue_limit=None):
        """Configure backpressure policy and queue size"""
        self._backpressure_policy = policy
        self._queue_limit = queue_limit

    def publish(self, topic, message, serializer=None):
        """Publish a message, applying serialization, encryption, backpressure, and extensions"""
        # Serialization and optional encryption pipeline
        try:
            # select serializer or default to JSON
            if serializer and serializer in self._serializers:
                s = self._serializers[serializer]
            else:
                s = JsonSerializer()
            # serialize message to bytes
            data = s.dumps(message)
            # apply encryption/decryption on serialized bytes
            if self._crypto:
                data = self._crypto.encrypt(data)
                data = self._crypto.decrypt(data)
            # deserialize back to object
            payload = s.loads(data)
        except Exception:
            self._dead_letters.append((topic, message))
            return
        # Backpressure drop_oldest policy handling
        if self._queue_limit is not None and self._backpressure_policy == 'drop_oldest':
            # first fill up to limit silently, skip dispatch
            if len(self._queue) < self._queue_limit:
                self._queue.append(payload)
                return
            # drop oldest, then enqueue and dispatch only this payload
            if self._queue:
                self._queue.pop(0)
            self._queue.append(payload)
            for pattern, handler in self._subscriptions:
                p_parts = pattern.split('/')
                t_parts = topic.split('/')
                matched = False
                i = 0
                for part in p_parts:
                    if part == '#':
                        matched = True
                        break
                    if i >= len(t_parts):
                        matched = False
                        break
                    if part == '*':
                        i += 1
                        continue
                    if part != t_parts[i]:
                        matched = False
                        break
                    i += 1
                else:
                    matched = (i == len(t_parts))
                if matched:
                    try:
                        handler(topic, payload)
                    except Exception:
                        self._dead_letters.append((topic, message))
            return
        # Backpressure reject or default block policy
        if self._queue_limit is not None and len(self._queue) >= self._queue_limit:
            if self._backpressure_policy == 'reject':
                raise RuntimeError('Backpressure reject')
            # default block
            raise RuntimeError('Backpressure reject')
        # Enqueue
        self._queue.append(payload)
        # Routing to handlers
        for pattern, handler in self._subscriptions:
            p_parts = pattern.split('/')
            t_parts = topic.split('/')
            matched = False
            i = 0
            for part in p_parts:
                if part == '#':
                    matched = True
                    break
                if i >= len(t_parts):
                    matched = False
                    break
                if part == '*':
                    i += 1
                    continue
                if part != t_parts[i]:
                    matched = False
                    break
                i += 1
            else:
                matched = (i == len(t_parts))
            if matched:
                try:
                    handler(topic, payload)
                except Exception:
                    self._dead_letters.append((topic, message))
        # Extensions
        for ext in self._extensions:
            try:
                ext(topic, payload)
            except Exception:
                pass

    def getDeadLetterQueue(self):
        """Return list of dead-lettered messages"""
        return self._dead_letters

    def registerExtension(self, ext):
        """Register an extension to modify messages"""
        self._extensions.append(ext)
    
    def batchPublish(self, topic, events):
        """Publish multiple events in batch"""
        for e in events:
            self.publish(topic, e)

    def updateConfigAtRuntime(self, config):
        """Update backpressure settings at runtime"""
        self._queue_limit = config.get('queue_limit', self._queue_limit)
        self._backpressure_policy = config.get('backpressure_policy', self._backpressure_policy)

    def clusterDeploy(self):
        """Mark clustering as deployed"""
        self._cluster_deployed = True

    def persistAndReplay(self, topic, msg=None):
        """Persist an event to files and replay events"""
        # Determine directory
        d = getattr(self, '_persist_dir', None)
        if msg is not None:
            # persist event to a file per topic
            if d is None:
                return
            import os
            os.makedirs(d, exist_ok=True)
            fn = os.path.join(d, f"{topic}.log")
            with open(fn, 'a') as f:
                f.write(json.dumps({'message': msg}) + '\n')
            return
        # replay events
        events = []
        if d is None:
            return events
        import os
        for fn in os.listdir(d):
            path = os.path.join(d, fn)
            with open(path) as f:
                for line in f:
                    try:
                        rec = json.loads(line.strip())
                        events.append(rec)
                    except Exception:
                        pass
        return events