"""
Trading Analyst EventBus facade implementing stubs generation, encryption, serializer registry, auth, context propagation, load balancing, schema validation, backpressure, clustering, and metrics.
"""
import time
import json


class EventBus:
    def __init__(self):
        # Serializer registry: name -> dict with serializer/deserializer
        self.serializers = {}
        # Authentication stub: only 'valid_token' accepted
        # Not used here
        # Context propagation not storing any state
        # Metrics storage
        self.metrics = {'queue_latency': []}

    def generate_stubs(self):
        # Return SDK stubs for cpp, java, python
        return {
            'cpp': '// C++ client stub code',
            'java': '// Java client stub code',
            'python': '# Python client stub code'
        }

    def encrypt_payload(self, data, key=None):
        # Simple XOR encryption for strings
        if key is None or not isinstance(data, str):
            return data
        k = ord(key[0])
        return ''.join(chr(ord(c) ^ k) for c in data)

    def register_serializer(self, name, serializer, deserializer):
        # Store serializer and deserializer
        self.serializers[name] = {
            'serializer': serializer,
            'deserializer': deserializer
        }

    def authenticate_actor(self, token):
        # Simplistic auth: only 'valid_token' accepted
        return token == 'valid_token'

    def propagate_context(self, event, context):
        # Merge event dict and context, add timestamp
        out = dict(event)
        out.update(context)
        out['timestamp'] = time.time()
        return out

    def balance_load(self, items, handlers):
        if not handlers:
            return {}
        dist = {h: [] for h in handlers}
        for idx, item in enumerate(items):
            h = handlers[idx % len(handlers)]
            dist[h].append(item)
        return dist

    def validate_schema(self, data, schema):
        # Validate presence of required fields
        for field in schema.get('fields', []):
            if field not in data:
                return False
        return True

    def control_backpressure(self, limit):
        # Trim or keep queue list to last 'limit' items
        # Operating on self.queue list
        q = getattr(self, 'queue', [])
        if len(q) > limit:
            q[:] = q[-limit:]
        return q

    def setup_clustering(self, nodes):
        if not nodes:
            return {'leader': None, 'followers': []}
        return {'leader': nodes[0], 'followers': nodes[1:]}

    def expose_metrics(self):
        # Return snapshot of metrics
        snap = {}
        for k, v in self.metrics.items():
            snap[k] = list(v) if isinstance(v, list) else v
        return snap