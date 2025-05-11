"""
Distributed Architect EventBus implementation
"""
import json
import threading
from . import jsonschema


class BufferError(Exception):
    """Raised when backpressure policy rejects an event"""
    pass


class EventBus:
    def __init__(self):
        # Serializer registry with default JSON
        self._serializers = {'json': (json.dumps, json.loads)}
        # Access control lists: topic -> [actors]
        self._acls = {}
        # Metrics counters
        self._counters = {}
        # Internal event queue for backpressure
        self._queue = []
        # Thread-local context storage
        self._local = threading.local()
        # Clustering nodes
        self.nodes = []
        self.leader = None
        # Backpressure settings
        self._bp_limit = None
        self._bp_policy = None

    def generateDocumentation(self):
        return {
            'serializers': list(self._serializers.keys()),
            'acls': dict(self._acls),
            'metrics': list(self._counters.keys())
        }

    def encryptPayload(self, payload, key=None):
        # Symmetric XOR encryption/decryption
        if isinstance(payload, str):
            data = payload.encode('utf-8')
        elif isinstance(payload, (bytes, bytearray)):
            data = bytes(payload)
        else:
            data = str(payload).encode('utf-8')
        if key is None:
            return data
        # Normalize key to bytes
        key_bytes = key if isinstance(key, (bytes, bytearray)) else bytes(key)
        k = key_bytes[0]
        return bytes([b ^ k for b in data])

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

    def registerSerializer(self, name, enc_fn, dec_fn):
        self._serializers[name] = (enc_fn, dec_fn)

    def authorizeActor(self, topic, actor):
        self._acls.setdefault(topic, []).append(actor)

    def checkAuthorization(self, topic, actor):
        return actor in self._acls.get(topic, [])

    def propagateContext(self, key, value):
        setattr(self._local, key, value)

    def getContext(self, key):
        return getattr(self._local, key, None)

    def balanceLoad(self, handlers, events):
        if not handlers:
            return {}
        dist = {h: [] for h in handlers}
        n = len(handlers)
        for idx, evt in enumerate(events):
            h = handlers[idx % n]
            dist[h].append(evt)
        return dist

    def validateSchema(self, schema, payload):
        # Uses distributed_architect.jsonschema
        jsonschema.validate(schema, payload)
        return True

    def controlBackpressure(self, limit, policy):
        self._bp_limit = limit
        self._bp_policy = policy

    def publish(self, event):
        # Backpressure enforcement
        if self._bp_limit is not None and len(self._queue) >= self._bp_limit:
            if self._bp_policy == 'reject':
                raise BufferError()
            elif self._bp_policy == 'drop_oldest':
                if self._queue:
                    self._queue.pop(0)
        self._queue.append(event)

    def setupClustering(self, nodes):
        if not nodes:
            raise ValueError("No nodes provided")
        self.nodes = list(nodes)
        self.leader = self.nodes[0]

    def getLeader(self):
        return self.leader

    def getCounter(self, name):
        return self._counters.get(name, 0)

    def incrementCounter(self, name, amount=1):
        self._counters[name] = self.getCounter(name) + amount

    def exposeMetrics(self):
        return {'counters': dict(self._counters)}