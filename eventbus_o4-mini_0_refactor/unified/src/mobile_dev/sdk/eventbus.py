"""
Mobile Development EventBus SDK for generating client stubs and handling payloads, auth, balancing, schema, backpressure, clustering, and metrics.
"""

class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass

class BackpressureError(Exception):
    """Raised on backpressure block policy overflow"""
    pass

class EventBusSDK:
    def __init__(self):
        # Serializer registry: name -> (dumps, loads)
        self._serializers = {}
        # Valid tokens
        self._valid_tokens = set()
        # Balance: use round-robin between local and remote
        self._rr_flag = 0
        # Internal metrics
        self.counters = {}
        self.histograms = {}
        # Backpressure settings
        self.queue_max_size = None
        self.drop_policy = False
        # Cluster endpoints
        self._cluster_endpoints = []

    def generateClientSDK(self):
        # Return dummy Swift and Kotlin SDK strings
        swift = '// Swift client SDK code'
        kotlin = '// Kotlin client SDK code'
        return swift, kotlin

    def encryptPayload(self, payload, key=None):
        # Simple XOR with first byte of key
        if key is None:
            return payload
        k = key[0] if isinstance(key, (bytes, bytearray)) else key
        return bytes(b ^ k for b in payload)

    def decryptPayload(self, payload, key=None):
        # symmetric XOR
        return self.encryptPayload(payload, key)

    def registerSerializer(self, name, dumps_fn, loads_fn):
        self._serializers[name] = (dumps_fn, loads_fn)

    def serialize(self, name, obj):
        if name not in self._serializers:
            raise KeyError(f"Serializer '{name}' not found")
        dumps, _ = self._serializers[name]
        return dumps(obj)

    def deserialize(self, name, data):
        if name not in self._serializers:
            raise KeyError(f"Serializer '{name}' not found")
        _, loads = self._serializers[name]
        return loads(data)

    def addValidToken(self, token):
        self._valid_tokens.add(token)

    def authenticateUser(self, token):
        if token in self._valid_tokens:
            return True
        raise AuthenticationError('Invalid token')

    def propagateContext(self, payload, **context):
        return {'payload': payload, 'context': context}

    def balanceLoad(self, item):
        # Alternate between local and remote
        choice = 'local' if self._rr_flag % 2 == 0 else 'remote'
        self._rr_flag += 1
        return choice, item

    def registerSchema(self, topic, schema):
        self._schemas = getattr(self, '_schemas', {})
        self._schemas[topic] = schema

    def validateSchema(self, topic, payload):
        schema = getattr(self, '_schemas', {}).get(topic)
        if not schema:
            return True
        # check required fields
        for key in schema.get('required', []):
            if key not in payload:
                from mobile_dev.jsonschema import ValidationError
                raise ValidationError(f"Missing required field '{key}'")
        return True

    def controlBackpressure(self, value):
        # initialize queue if needed
        if self.queue_max_size is None:
            return True
        self.counters.setdefault('control_calls', 0)
        # track calls not needed
        if not hasattr(self, '_bp_queue'):
            self._bp_queue = []
        if len(self._bp_queue) < self.queue_max_size:
            self._bp_queue.append(value)
            return True
        # queue full
        if self.drop_policy:
            return False
        raise BackpressureError('Queue full')

    def setupClustering(self, endpoints):
        self._cluster_endpoints = list(endpoints)

    def sendViaCluster(self, message, sender_func):
        last_exc = None
        for ep in self._cluster_endpoints:
            try:
                return sender_func(ep, message)
            except Exception as e:
                last_exc = e
                continue
        raise RuntimeError('All endpoints failed')

    def exposeMetrics(self, name, value=None):
        if value is None:
            # counter
            self.counters[name] = self.counters.get(name, 0) + 1
        else:
            self.histograms.setdefault(name, []).append(value)