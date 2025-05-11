import json
import threading
from collections import deque, defaultdict
from jsonschema import validate, ValidationError

class AuthenticationError(Exception):
    pass

class BackpressureError(Exception):
    pass

class EventBusSDK:
    def __init__(self):
        self.serializers = {}
        self.valid_tokens = set()
        self.schemas = {}
        self.queue = deque()
        self.queue_lock = threading.Lock()
        self.queue_max_size = 100
        self.drop_policy = True
        self.cluster_endpoints = []
        self.current_endpoint = 0
        self.counters = defaultdict(int)
        self.histograms = defaultdict(list)
        self.local_count = 0
        self.remote_count = 0

    def generateClientSDK(self):
        swift = "// Swift client SDK stub\npublic class EventBusClient {}"
        kotlin = "// Kotlin client SDK stub\nclass EventBusClient {}"
        return swift, kotlin

    def encryptPayload(self, payload: bytes, key: bytes) -> bytes:
        # Simple XOR cipher for demonstration
        return bytes([b ^ key[i % len(key)] for i, b in enumerate(payload)])

    def decryptPayload(self, encrypted: bytes, key: bytes) -> bytes:
        # XOR decryption is symmetric
        return bytes([b ^ key[i % len(key)] for i, b in enumerate(encrypted)])

    def registerSerializer(self, name: str, serialize_fn, deserialize_fn):
        self.serializers[name] = (serialize_fn, deserialize_fn)

    def serialize(self, name: str, obj):
        if name not in self.serializers:
            raise KeyError(f"No serializer registered under '{name}'")
        sfn, _ = self.serializers[name]
        return sfn(obj)

    def deserialize(self, name: str, data):
        if name not in self.serializers:
            raise KeyError(f"No serializer registered under '{name}'")
        _, dfn = self.serializers[name]
        return dfn(data)

    def authenticateUser(self, token: str):
        if token not in self.valid_tokens:
            raise AuthenticationError("Invalid token")
        return True

    def addValidToken(self, token: str):
        self.valid_tokens.add(token)

    def propagateContext(self, payload, correlation_id=None, user_id=None, performance_marks=None):
        ctx = {
            "correlation_id": correlation_id,
            "user_id": user_id,
            "performance_marks": performance_marks or {}
        }
        return {"payload": payload, "context": ctx}

    def balanceLoad(self, message):
        # simple round-robin between local and remote
        total = self.local_count + self.remote_count
        if total % 2 == 0:
            self.local_count += 1
            return "local", message
        else:
            self.remote_count += 1
            return "remote", message

    def validateSchema(self, topic: str, message: dict):
        if topic not in self.schemas:
            return True
        schema = self.schemas[topic]
        validate(instance=message, schema=schema)
        return True

    def registerSchema(self, topic: str, schema: dict):
        self.schemas[topic] = schema

    def controlBackpressure(self, message):
        with self.queue_lock:
            if len(self.queue) < self.queue_max_size:
                self.queue.append(message)
                return True
            else:
                if self.drop_policy:
                    return False
                else:
                    raise BackpressureError("Queue is full")

    def setupClustering(self, endpoints: list):
        self.cluster_endpoints = endpoints
        self.current_endpoint = 0

    def sendViaCluster(self, message, sender_fn):
        if not self.cluster_endpoints:
            raise RuntimeError("No cluster endpoints configured")
        attempts = len(self.cluster_endpoints)
        for _ in range(attempts):
            endpoint = self.cluster_endpoints[self.current_endpoint]
            try:
                return sender_fn(endpoint, message)
            except Exception:
                self.current_endpoint = (self.current_endpoint + 1) % len(self.cluster_endpoints)
        raise RuntimeError("All endpoints failed")

    def exposeMetrics(self, name: str, value: float = None):
        if value is None:
            self.counters[name] += 1
        else:
            self.histograms[name].append(value)
        return True
