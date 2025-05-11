"""
Quant Trader EventBus with subscription, wildcard matching, retry, crypto, serializers, backpressure, batching, clustering, persistence, and extensions
"""
import json


class SimpleJSONSerializer:
    """Simple JSON serializer/deserializer"""
    def serialize(self, event):
        return json.dumps(event)
    def deserialize(self, payload):
        return json.loads(payload)


class EventBus:
    def __init__(self):
        # Subscription patterns: pattern -> [handlers]
        self._subscriptions = {}
        # Event queue: list of dicts {topic, event, attempts}
        self.event_queue = []
        # Dead letter storage
        self._dead_letters = []
        # Default serializer name or instance
        self.default_serializer = None
        # Registered serializers: name -> instance
        self._serializers = {'json': SimpleJSONSerializer()}
        # Crypto module
        self._crypto = None
        # Retry attempts for processing
        self.max_retries = 1
        # Backpressure
        self.queue_limit = None
        self.bp_policy = None
        # Batch processing size
        self.batch_size = None
        # Extensions: functions modifying payload
        self._extensions = []
        # Persistence
        self._persisted = []
        # Clustering
        self.cluster_nodes = []
        self.leader = None

    def subscribe(self, pattern, handler):
        self._subscriptions.setdefault(pattern, []).append(handler)

    def registerCryptoModule(self, crypto):
        self._crypto = crypto

    def registerSerializer(self, name, serializer):
        self._serializers[name] = serializer

    def applyBackpressure(self, limit=None, policy=None):
        self.queue_limit = limit
        self.bp_policy = policy

    def batchPublish(self, size):
        self.batch_size = size

    def updateConfigAtRuntime(self, max_retries=None, queue_limit=None):
        if max_retries is not None:
            self.max_retries = max_retries
        if queue_limit is not None:
            self.queue_limit = queue_limit

    def clusterDeploy(self, nodes):
        self.cluster_nodes = list(nodes)
        self.leader = nodes[0] if nodes else None
        return {'leader': self.leader, 'followers': nodes[1:] if len(nodes) > 1 else []}

    def publish(self, topic, event):
        # Backpressure enforcement
        if self.queue_limit is not None and len(self.event_queue) >= self.queue_limit:
            if self.bp_policy == 'reject':
                raise Exception('Backpressure reject')
            elif self.bp_policy == 'drop_oldest':
                # if queue_limit zero, drop without enqueue
                if self.queue_limit == 0:
                    return
                # remove oldest
                if self.event_queue:
                    self.event_queue.pop(0)
        # Persist event for replay
        self._persisted.append({'topic': topic, 'event': event})
        # Enqueue for processing with attempt count
        self.event_queue.append({'topic': topic, 'event': event, 'attempts': 0})

    def process_queue(self):
        # Batch processing per topic if batch_size set
        if self.batch_size:
            # group events by topic
            topics = {}
            for rec in self.event_queue:
                topics.setdefault(rec['topic'], []).append(rec)
            for topic, recs in topics.items():
                if len(recs) >= self.batch_size:
                    # collect raw events
                    payloads = [r['event'] for r in recs]
                    # serialize
                    ser = self._serializers.get(self.default_serializer, self._serializers['json'])
                    data = ser.serialize(payloads)
                    # crypto
                    if self._crypto:
                        data = self._crypto.encrypt(data)
                    # extensions
                    for ext in self._extensions:
                        try:
                            data = ext(data)
                        except Exception:
                            pass
                    # dispatch handlers
                    for pattern, handlers in self._subscriptions.items():
                        if self._match(pattern, topic):
                            for h in handlers:
                                h(data)
                    # remove processed records
                    self.event_queue = [r for r in self.event_queue if r['topic'] != topic]
                    # do not proceed to normal processing
                    return
        # Process all queued events
        if not self.event_queue:
            return
        old_queue = list(self.event_queue)
        self.event_queue.clear()
        for rec in old_queue:
            topic = rec['topic']
            event = rec['event']
            rec['attempts'] = rec.get('attempts', 0) + 1
            try:
                # apply crypto to raw event before serialization
                payload = event
                if self._crypto:
                    payload = self._crypto.encrypt(payload)
                # serialize
                ser = self._serializers.get(self.default_serializer, self._serializers['json'])
                data = ser.serialize(payload)
                # extensions
                for ext in self._extensions:
                    try:
                        data = ext(data)
                    except Exception:
                        pass
                # dispatch handlers
                for pattern, handlers in self._subscriptions.items():
                    if self._match(pattern, topic):
                        for h in handlers:
                            h(data)
                # successful processing: do not requeue
                continue
            except Exception:
                # failure: determine retry or dead-letter
                if rec['attempts'] <= self.max_retries:
                    self.event_queue.append(rec)
                else:
                    self._dead_letters.append({'topic': topic, 'event': event})

    def routeToDeadLetterQueue(self):
        return list(self._dead_letters)

    def persistAndReplay(self, start_index=0):
        return self._persisted[start_index:]

    def registerExtension(self, ext):
        self._extensions.append(ext)

    def _match(self, pattern, topic):
        p_parts = pattern.split('.')
        t_parts = topic.split('.')
        i = 0
        for part in p_parts:
            if part == '#':
                return True
            if i >= len(t_parts):
                return False
            if part == '*':
                i += 1
                continue
            if part != t_parts[i]:
                return False
            i += 1
        return i == len(t_parts)