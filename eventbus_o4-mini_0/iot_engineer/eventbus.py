import collections

class IoTEventBus:
    def __init__(self, max_queue_size=10):
        self.serializers = {}
        self.encryption_module = None
        self.device_tokens = {}
        self.handlers = []
        self.handler_index = 0
        self.schema = {}
        self.queue = collections.deque(maxlen=max_queue_size)
        self.cluster_nodes = []
        self.event_count = 0
        self.latencies = []

    def generateStubs(self):
        """
        Auto-generate client library stubs for registered serializers.
        Returns a dict mapping serializer names to stub code.
        """
        return {name: f"# Stub for serializer '{name}'" for name in self.serializers}

    def registerSerializer(self, name, serializer):
        """
        Register a serializer under a given name.
        """
        self.serializers[name] = serializer

    def setEncryptionModule(self, module):
        """
        Swap-in crypto module for payload encryption.
        The module must provide encrypt() and decrypt() methods.
        """
        self.encryption_module = module

    def encryptPayload(self, payload):
        """
        Encrypt payload using the configured encryption module.
        """
        if self.encryption_module:
            return self.encryption_module.encrypt(payload)
        return payload

    def authorizeDevice(self, device_id, token):
        """
        Token-based authentication: returns True if token matches stored token.
        """
        return self.device_tokens.get(device_id) == token

    def registerDeviceToken(self, device_id, token):
        """
        Store token for a device.
        """
        self.device_tokens[device_id] = token

    def propagateContext(self, event, context):
        """
        Attach context metadata to an event.
        """
        event = dict(event)  # shallow copy
        event['context'] = context
        return event

    def balanceLoad(self, handler):
        """
        Register an event handler for round-robin dispatch.
        """
        self.handlers.append(handler)

    def dispatchEvent(self, event):
        """
        Enqueue event (dropping oldest if full) and dispatch to a handler.
        Returns the handler invoked (or None).
        """
        self.queue.append(event)
        handler = None
        if self.handlers:
            idx = self.handler_index % len(self.handlers)
            handler = self.handlers[idx]
            self.handler_index += 1
            handler(event)
        self.event_count += 1
        return handler

    def setSchema(self, schema):
        """
        Set a simple schema: dict of field->type for validation.
        """
        self.schema = schema

    def validateSchema(self, payload):
        """
        Validate payload against the stored schema.
        Returns True if valid, False otherwise.
        """
        for field, expected_type in self.schema.items():
            if field not in payload or not isinstance(payload[field], expected_type):
                return False
        return True

    def controlBackpressure(self):
        """
        Return the current queue length (buffer state).
        """
        return len(self.queue)

    def setupClustering(self, nodes):
        """
        Configure cluster nodes for failover.
        """
        self.cluster_nodes = list(nodes)

    def exposeMetrics(self):
        """
        Return current metrics: event count, queue length, avg latency.
        """
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
        return {
            'event_count': self.event_count,
            'queue_length': len(self.queue),
            'average_latency': avg_latency
        }

    def recordLatency(self, latency):
        """
        Record processing latency for metrics.
        """
        self.latencies.append(latency)
