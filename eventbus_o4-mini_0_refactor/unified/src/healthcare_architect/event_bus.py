"""
Healthcare Architect EventBus with context, backpressure, serialization, clustering, and extensions
"""
from collections import defaultdict


class Event:
    """Represents an event with id, payload, and routing key"""
    def __init__(self, id, payload, routing_key):
        self.id = id
        self.payload = payload
        self.routing_key = routing_key


class EventBus:
    def __init__(self):
        # Wildcard subscriptions: pattern -> [handlers]
        self._subscriptions = defaultdict(list)
        # Dead letter queue entries
        self.dead_letter_queue = []
        # Crypto module
        self._crypto = None
        # Backpressure settings
        self.backpressure_limit = None
        self.backpressure_policy = None
        # Internal queue of events
        self.queue = []
        # Serializer registry: name -> serializer instance
        self._serializers = {}
        # Configuration
        self.config = {}
        # Extensions
        self._extensions = []
        # Persistent store for replay
        self._persisted = []

    def subscribeWildcard(self, pattern, handler):
        self._subscriptions[pattern].append(handler)

    def registerCryptoModule(self, crypto):
        self._crypto = crypto

    def applyBackpressure(self, limit, policy):
        self.backpressure_limit = limit
        self.backpressure_policy = policy

    def registerSerializer(self, name, serializer):
        self._serializers[name] = serializer

    def serialize(self, name, event):
        if name not in self._serializers:
            raise ValueError(f"Serializer '{name}' not found")
        return self._serializers[name].serialize(event)

    def publish(self, event, topic):
        # Missing payload
        if event.payload is None:
            self.dead_letter_queue.append({'event': event, 'reason': 'missing_payload'})
            return
        # Apply backpressure
        if self.backpressure_limit is not None and len(self.queue) >= self.backpressure_limit:
            if self.backpressure_policy == 'drop_oldest':
                if self.queue:
                    self.queue.pop(0)
            elif self.backpressure_policy == 'reject':
                return
        # Encrypt payload if module exists
        if self._crypto:
            try:
                event.payload = self._crypto.encrypt(event.payload)
            except Exception:
                pass
        # Store in queue
        self.queue.append(event)
        # Persist for replay
        self._persisted.append(event)
        # Apply extensions before invoking handlers
        for ext in self._extensions:
            try:
                ext(event)
            except Exception:
                pass
        # Invoke handlers
        for pattern, handlers in self._subscriptions.items():
            # wildcard match
            parts = pattern.split('.')
            tparts = topic.split('.')
            def match(pats, tps):
                i = 0
                for p in pats:
                    if p == '#':
                        return True
                    if i >= len(tps):
                        return False
                    if p == '*':
                        i += 1
                        continue
                    if p != tps[i]:
                        return False
                    i += 1
                return i == len(tps)
            if match(parts, tparts):
                for handler in handlers:
                    try:
                        handler(event)
                    except Exception:
                        self.dead_letter_queue.append({'event': event, 'reason': 'handler_exception'})

    def batchPublish(self, events):
        for ev in events:
            self.publish(ev, ev.routing_key)

    def updateConfigAtRuntime(self, backpressure_limit=None, backpressure_policy=None, timeout=None):
        if backpressure_limit is not None:
            self.backpressure_limit = backpressure_limit
        if backpressure_policy is not None:
            self.backpressure_policy = backpressure_policy
        if timeout is not None:
            self.config['timeout'] = timeout

    def clusterDeploy(self, nodes):
        leader = nodes[0] if nodes else None
        stores = {}
        for n in nodes:
            # copy current queue
            stores[n] = list(self.queue)
        self.cluster = {'leader': leader, 'replicated_stores': stores}
        return self.cluster

    def persistAndReplay(self, start_index=0):
        # Return list of events from start_index
        return self._persisted[start_index:]

    def registerExtension(self, ext):
        self._extensions.append(ext)