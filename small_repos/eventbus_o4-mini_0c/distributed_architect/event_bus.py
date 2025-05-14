import json
import threading
import collections
from builtins import BufferError
import jsonschema

class EventBus:
    def __init__(self):
        self.serializers = {'json': (json.dumps, json.loads)}
        self.acls = collections.defaultdict(set)
        self._context = threading.local()
        # initialize for the creating thread
        self._context.data = {}
        self.backpressure_limit = None
        self.backpressure_policy = None
        self._queue = collections.deque()
        self.nodes = []
        self.leader = None
        self.metrics = {
            'counters': {},
            'gauges': {},
            'histograms': {}
        }

    def generateDocumentation(self):
        return {
            'serializers': list(self.serializers.keys()),
            'acls': {topic: list(actors) for topic, actors in self.acls.items()},
            'metrics': list(self.metrics['counters'].keys())
        }

    def encryptPayload(self, payload, key: bytes = None):
        if isinstance(payload, str):
            payload = payload.encode('utf-8')
        if key is None:
            key = b'default_secret_key'
        key_len = len(key)
        encrypted = bytes([b ^ key[i % key_len] for i, b in enumerate(payload)])
        return encrypted

    def registerSerializer(self, name, encoder, decoder):
        self.serializers[name] = (encoder, decoder)

    def serialize(self, name, obj):
        if name not in self.serializers:
            raise KeyError(f"Serializer '{name}' not registered")
        encoder, _ = self.serializers[name]
        return encoder(obj)

    def deserialize(self, name, data):
        if name not in self.serializers:
            raise KeyError(f"Serializer '{name}' not registered")
        _, decoder = self.serializers[name]
        return decoder(data)

    def authorizeActor(self, topic, actor):
        self.acls[topic].add(actor)

    def checkAuthorization(self, topic, actor):
        return actor in self.acls.get(topic, set())

    def propagateContext(self, key, value):
        if not hasattr(self._context, 'data'):
            self._context.data = {}
        self._context.data[key] = value

    def getContext(self, key):
        return getattr(self._context, 'data', {}).get(key)

    def balanceLoad(self, handlers, events):
        if not handlers:
            return {}
        distribution = {h: [] for h in handlers}
        for idx, event in enumerate(events):
            handler = handlers[idx % len(handlers)]
            distribution[handler].append(event)
        return distribution

    def validateSchema(self, schema, payload):
        # will raise jsonschema.ValidationError on failure
        jsonschema.validate(instance=payload, schema=schema)
        return True

    def controlBackpressure(self, limit, policy='reject'):
        if policy not in ('block', 'drop_oldest', 'reject'):
            raise ValueError("Policy must be one of 'block', 'drop_oldest', 'reject'")
        self.backpressure_limit = limit
        self.backpressure_policy = policy

    def publish(self, event):
        if self.backpressure_limit is None:
            self._queue.append(event)
            return
        if len(self._queue) < self.backpressure_limit:
            self._queue.append(event)
        else:
            if self.backpressure_policy == 'reject':
                raise BufferError("Backpressure: queue is full")
            elif self.backpressure_policy == 'drop_oldest':
                self._queue.popleft()
                self._queue.append(event)
            elif self.backpressure_policy == 'block':
                # simplistic block: spin-wait until space
                import time
                while len(self._queue) >= self.backpressure_limit:
                    time.sleep(0.01)
                self._queue.append(event)

    def setupClustering(self, nodes):
        if not nodes:
            raise ValueError("At least one node is required")
        self.nodes = list(nodes)
        self.leader = self.nodes[0]

    def getLeader(self):
        return self.leader

    def exposeMetrics(self):
        return self.metrics

    def incrementCounter(self, name, value=1):
        self.metrics['counters'].setdefault(name, 0)
        self.metrics['counters'][name] += value

    def getCounter(self, name):
        return self.metrics['counters'].get(name, 0)
