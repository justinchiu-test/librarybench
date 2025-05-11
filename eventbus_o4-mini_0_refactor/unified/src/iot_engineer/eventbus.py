"""
IoT Engineer specific EventBus implementation
"""
from collections import deque


class IoTEventBus:
    def __init__(self, max_queue_size=None):
        # Serializer registry: name -> serializer instance
        self._serializers = {}
        # Encryption module
        self._crypto = None
        # Device tokens
        self._device_tokens = {}
        # Context propagation
        # Handler pool
        self._handlers = []
        self._dispatch_index = 0
        # Event counter
        self.event_count = 0
        # Queuing for backpressure
        # Use deque to auto-drop oldest when maxlen
        if max_queue_size:
            self._queue = deque(maxlen=max_queue_size)
        else:
            self._queue = deque()
        # Latency records
        self._latencies = []
        # Clustering nodes
        self.cluster_nodes = []

    def registerSerializer(self, name, serializer):
        self._serializers[name] = serializer

    def generateStubs(self):
        # Generate code stubs for each serializer
        stubs = {}
        for name in self._serializers:
            stubs[name] = f"# Stub for serializer '{name}'"
        return stubs

    def encryptPayload(self, payload):
        # No encryption by default
        if self._crypto:
            return self._crypto.encrypt(payload)
        return payload

    def setEncryptionModule(self, crypto):
        self._crypto = crypto

    def registerDeviceToken(self, device_id, token):
        self._device_tokens[device_id] = token

    def authorizeDevice(self, device_id, token):
        return self._device_tokens.get(device_id) == token

    def propagateContext(self, event, context):
        new_event = dict(event)
        new_event['context'] = context
        return new_event

    def balanceLoad(self, handler):
        self._handlers.append(handler)

    def dispatchEvent(self, event):
        # Enqueue event for backpressure before dispatch
        self._queue.append(event)
        # Increment event count
        self.event_count += 1
        # Round-robin dispatch if handlers are available
        if not self._handlers:
            return None
        handler = self._handlers[self._dispatch_index % len(self._handlers)]
        self._dispatch_index += 1
        handler(event)
        return handler

    def setSchema(self, schema):
        # Accept a type mapping for simple validation
        self._schema = schema

    def validateSchema(self, data):
        # Validate against simple type mapping
        # schema: {key: type}
        for key, typ in self._schema.items():
            if key not in data or not isinstance(data[key], typ):
                return False
        return True

    def controlBackpressure(self):
        # Return current queue length
        return len(self._queue)

    def setupClustering(self, nodes):
        self.cluster_nodes = list(nodes)

    def recordLatency(self, value):
        self._latencies.append(value)

    def exposeMetrics(self):
        # Compute average latency
        count = self.event_count
        qlen = len(self._queue)
        avg = sum(self._latencies) / len(self._latencies) if self._latencies else 0
        return {'event_count': count, 'queue_length': qlen, 'average_latency': avg}