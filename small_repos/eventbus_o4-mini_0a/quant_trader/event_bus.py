import time
from collections import deque, defaultdict

class SimpleJSONSerializer:
    def serialize(self, event):
        import json
        return json.dumps(event)
    def deserialize(self, payload):
        import json
        return json.loads(payload)

class EventBus:
    def __init__(self):
        self.subscriptions = []  # list of (pattern, callback)
        self.event_queue = deque()
        self.dead_letter_queue = []
        self.persistent_store = []
        self.serializers = {'default': SimpleJSONSerializer()}
        self.default_serializer = 'default'
        self.crypto_module = None
        self.queue_limit = 1000
        self.backpressure_policy = 'block'  # block, drop_oldest, reject
        self.max_retries = 3
        self.batch_size = 1
        self.batch_buffers = defaultdict(list)
        self.extensions = []
        self.cluster_nodes = []
        self.leader = None

    def subscribe(self, pattern, callback):
        self.subscriptions.append((pattern, callback))

    def _match(self, pattern, topic):
        p = pattern.split('.')
        t = topic.split('.')
        return self._match_helper(p, t)

    def _match_helper(self, p, t):
        if not p:
            return not t
        if p[0] == '#':
            return True
        if not t:
            return False
        if p[0] == '*' or p[0] == t[0]:
            return self._match_helper(p[1:], t[1:])
        return False

    def publish(self, topic, event):
        # handle batch
        if self.batch_size > 1:
            buf = self.batch_buffers[topic]
            buf.append(event)
            if len(buf) < self.batch_size:
                return
            event = list(buf)
            self.batch_buffers[topic] = []
        # backpressure
        if len(self.event_queue) >= self.queue_limit:
            if self.backpressure_policy == 'block':
                while len(self.event_queue) >= self.queue_limit:
                    time.sleep(0.001)
            elif self.backpressure_policy == 'drop_oldest':
                self.event_queue.popleft()
            elif self.backpressure_policy == 'reject':
                raise Exception('Backpressure: queue full')
        self.event_queue.append({'topic': topic, 'event': event, 'retries': 0})

    def process_queue(self):
        while self.event_queue:
            item = self.event_queue.popleft()
            topic = item['topic']
            event = item['event']
            # persist
            self.persistent_store.append({'topic': topic, 'event': event})
            # encrypt
            if self.crypto_module:
                event = self.crypto_module.encrypt(event)
            # serialize
            serializer = self.serializers.get(self.default_serializer)
            payload = serializer.serialize(event)
            # apply extensions
            for ext in self.extensions:
                modified = ext(payload)
                if modified is not None:
                    payload = modified
            # dispatch
            for pattern, callback in self.subscriptions:
                if self._match(pattern, topic):
                    try:
                        callback(payload)
                    except Exception:
                        item['retries'] += 1
                        if item['retries'] < self.max_retries:
                            self.event_queue.append(item)
                        else:
                            self.dead_letter_queue.append(item)

    def routeToDeadLetterQueue(self):
        return self.dead_letter_queue

    def registerSerializer(self, name, serializer):
        self.serializers[name] = serializer

    def registerCryptoModule(self, crypto_module):
        self.crypto_module = crypto_module

    def applyBackpressure(self, limit, policy):
        self.queue_limit = limit
        self.backpressure_policy = policy

    def batchPublish(self, batch_size):
        self.batch_size = batch_size

    def updateConfigAtRuntime(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def clusterDeploy(self, nodes):
        self.cluster_nodes = nodes
        if nodes:
            self.leader = nodes[0]

    def persistAndReplay(self):
        for record in self.persistent_store:
            yield record

    def registerExtension(self, extension):
        self.extensions.append(extension)
