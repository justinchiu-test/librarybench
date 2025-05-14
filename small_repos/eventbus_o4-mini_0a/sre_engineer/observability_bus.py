import queue
import json
from types import MappingProxyType

class IdentityCrypto:
    def encrypt(self, data):
        return data
    def decrypt(self, data):
        return data

class JSONSerializer:
    def serialize(self, event):
        return json.dumps(event)
    def deserialize(self, data):
        return json.loads(data)

class ObservabilityEventBus:
    def __init__(self, config=None):
        # internal mutable config
        self._config = {
            'queue_size': 1000,
            'backpressure_policy': 'block',  # block, drop_oldest, reject
            'batch_size': 10,
            'persist_file': 'events.log'
        }
        if config:
            self._config.update(config)
        # initialize queue with configured size
        self.queue = queue.Queue(maxsize=self._config['queue_size'])
        self.subscriptions = {}  # pattern -> [callbacks]
        self.dead_letter_queue = []
        self.serializers = {}
        self.registerSerializer('json', JSONSerializer())
        self.default_crypto = IdentityCrypto()
        self.extensions = []
        self.batch_queues = {}  # topic -> list of (topic,event,serializer,encrypt)
        self.cluster_nodes = []
        self.leader = None

    @property
    def config(self):
        # expose a read-only view of the config
        return MappingProxyType(self._config)

    def registerSerializer(self, name, serializer):
        self.serializers[name] = serializer

    def registerCrypto(self, crypto_module):
        self.default_crypto = crypto_module

    def subscribeWildcard(self, pattern, callback):
        self.subscriptions.setdefault(pattern, []).append(callback)

    def _match(self, pattern, topic):
        p = pattern.split('.') if pattern else []
        t = topic.split('.') if topic else []
        i = j = 0
        while i < len(p) and j < len(t):
            if p[i] == '#':
                return True
            elif p[i] == '*':
                i += 1; j += 1
            elif p[i] == t[j]:
                i += 1; j += 1
            else:
                return False
        if i == len(p) and j == len(t):
            return True
        if i == len(p)-1 and p[i] == '#':
            return True
        return False

    def routeToDeadLetterQueue(self, message):
        self.dead_letter_queue.append(message)

    def applyBackpressure(self, item):
        policy = self._config['backpressure_policy']
        if policy == 'block':
            self.queue.put(item)
        elif policy == 'drop_oldest':
            if self.queue.full():
                try:
                    self.queue.get_nowait()
                except queue.Empty:
                    pass
            self.queue.put_nowait(item)
        elif policy == 'reject':
            if self.queue.full():
                raise Exception('Queue full')
            self.queue.put_nowait(item)
        else:
            # unknown policy, default to block
            self.queue.put(item)

    def publish(self, topic, event, serializer='json', encrypt=False):
        for ext in self.extensions:
            event = ext(event, topic)
        if serializer not in self.serializers:
            raise Exception('Serializer not found')
        data = self.serializers[serializer].serialize(event)
        if encrypt:
            data = self.default_crypto.encrypt(data)
        try:
            self.applyBackpressure((topic, serializer, data, encrypt))
        except Exception as e:
            self.routeToDeadLetterQueue({'topic': topic, 'event': event, 'error': str(e)})
            return False
        self._persist(topic, event)
        return True

    def process(self):
        while True:
            try:
                topic, serializer, data, encrypt = self.queue.get_nowait()
            except queue.Empty:
                break
            if encrypt:
                data = self.default_crypto.decrypt(data)
            event = self.serializers[serializer].deserialize(data)
            for pattern, callbacks in self.subscriptions.items():
                if self._match(pattern, topic):
                    for cb in callbacks:
                        try:
                            cb(topic, event)
                        except Exception as e:
                            self.routeToDeadLetterQueue({'topic': topic, 'event': event, 'error': str(e)})

    def batchPublish(self, topic, event, serializer='json', encrypt=False):
        lst = self.batch_queues.setdefault(topic, [])
        lst.append((topic, event, serializer, encrypt))
        if len(lst) >= self._config['batch_size']:
            self._flush_batch(topic)

    def _flush_batch(self, topic):
        lst = self.batch_queues.pop(topic, [])
        for _, event, serializer, encrypt in lst:
            self.publish(topic, event, serializer, encrypt)

    def updateConfigAtRuntime(self, key, value):
        # update internal config
        self._config[key] = value
        if key == 'queue_size':
            old_items = []
            while True:
                try:
                    old_items.append(self.queue.get_nowait())
                except queue.Empty:
                    break
            # recreate queue with new size
            self.queue = queue.Queue(maxsize=self._config['queue_size'])
            for item in old_items:
                try:
                    self.queue.put_nowait(item)
                except queue.Full:
                    break

    def registerExtension(self, extension):
        self.extensions.append(extension)

    def _persist(self, topic, event):
        fn = self._config['persist_file']
        with open(fn, 'a') as f:
            f.write(json.dumps({'topic': topic, 'event': event}) + '\n')

    def persistAndReplay(self, subscriber=None, file=None):
        fn = file or self._config['persist_file']
        events = []
        with open(fn, 'r') as f:
            for line in f:
                obj = json.loads(line.strip())
                events.append(obj)
        for obj in events:
            topic = obj['topic']
            event = obj['event']
            if subscriber:
                subscriber(topic, event)
            else:
                self.publish(topic, event)
        return events

    def clusterDeploy(self, nodes):
        self.cluster_nodes = list(nodes)
        self.leader = min(self.cluster_nodes)
        return self.leader
