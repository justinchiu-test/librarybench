"""
Healthcare Engineer EventBus with serialization, auth, context, backpressure, clustering, and metrics
"""
import uuid
import threading
from collections import defaultdict


class EventBus:
    def __init__(self):
        # Serializer registry: name -> (encode_fn, decode_fn)
        self._serializers = {}
        # Topic to schema mapping
        self._schemas = {}
        # Topic to queue mapping for backpressure
        self._queues = {}
        # Backpressure settings per topic
        self._bp_max = {}
        # Context storage
        self._context = {}
        # Worker pools for named tasks
        self._workers = {}
        self._rr_index = {}
        # Metrics data: counts and lists
        self.metrics_data = {
            'validation_errors': 0,
            'processing_latencies': []
        }
        # Clustering nodes
        self.cluster_nodes = []

    def register_serializer(self, name, encode_fn, decode_fn):
        self._serializers[name] = (encode_fn, decode_fn)

    def generate_documentation(self):
        return {'openapi': {}, 'sdks': ['python']}

    def encrypt_payload(self, data):
        # Identity encryption
        return data

    def decrypt_payload(self, data):
        # Identity decryption
        return data

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

    def set_topic_scopes(self, topic, scopes):
        self._scopes = getattr(self, '_scopes', {})
        self._scopes[topic] = set(scopes)

    def create_token(self, user, scopes):
        # token is a dict
        return {'user': user, 'scopes': list(scopes)}

    def authorize_user(self, token, topic):
        allowed = self._scopes.get(topic, set())
        return set(token.get('scopes', [])).issuperset(allowed)

    def propagate_context(self, event, context):
        new_event = dict(event)
        new_event['_context'] = context
        return new_event

    def configure_workers(self, name, workers):
        self._workers[name] = list(workers)
        self._rr_index[name] = 0

    def balance_load(self, name, event):
        lst = self._workers.get(name, [])
        if not lst:
            return None
        idx = self._rr_index.get(name, 0)
        worker = lst[idx % len(lst)]
        self._rr_index[name] = idx + 1
        return worker

    def register_schema(self, topic, schema):
        self._schemas[topic] = schema
        self._queues[topic] = []

    def validate_schema(self, topic, payload):
        """
        Validate payload against registered schema. Returns True if valid, False otherwise.
        """
        schema = self._schemas.get(topic)
        # Only support object type validation
        try:
            if schema.get('type') == 'object':
                if not isinstance(payload, dict):
                    raise ValueError('Payload is not object')
                for key in schema.get('required', []):
                    if key not in payload:
                        raise ValueError(f"Missing required field '{key}'")
                for prop, subs in schema.get('properties', {}).items():
                    if prop in payload:
                        expected = subs.get('type')
                        val = payload[prop]
                        if expected == 'number' and not isinstance(val, (int, float)):
                            raise ValueError(f"Field '{prop}' is not a number")
                        if expected == 'string' and not isinstance(val, str):
                            raise ValueError(f"Field '{prop}' is not a string")
            # Valid
            return True
        except Exception:
            # count validation error
            self.metrics_data['validation_errors'] += 1
            return False

    def set_backpressure(self, topic, max_size=0):
        # initialize queue if not exists
        self._queues.setdefault(topic, [])
        self._bp_max[topic] = max_size

    def control_backpressure(self, topic):
        q = self._queues.get(topic, [])
        max_size = self._bp_max.get(topic)
        if max_size is None:
            return True
        if len(q) >= max_size:
            raise OverflowError('Backpressure overflow')
        # simulate adding an item
        q.append(None)
        return True

    def setup_clustering(self, nodes):
        self.cluster_nodes = list(nodes)

    def expose_metrics(self):
        # return a shallow copy
        return dict(self.metrics_data)