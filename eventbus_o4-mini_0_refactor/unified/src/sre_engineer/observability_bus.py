"""
ObservabilityEventBus for SRE Engineer domain
"""
import json


class IdentityCrypto:
    """No-op cryptography"""
    def encrypt(self, data):
        return data
    def decrypt(self, data):
        return data

class ObservabilityEventBus:
    def __init__(self, config=None):
        # Configuration options
        cfg = config or {}
        self.config = cfg
        self.queue_size = cfg.get('queue_size')
        self.bp_policy = cfg.get('backpressure_policy')
        self.batch_size = cfg.get('batch_size')
        # Event queue
        self._queue = []
        # Dead letter queue for callback exceptions or rejects
        self.dead_letter_queue = []
        # Subscriptions: pattern -> [handler]
        self._subscriptions = {}
        # Crypto module
        self._crypto = None
        # Serializer registry
        self._serializers = {}
        # Extensions
        self._extensions = []

    def subscribeWildcard(self, pattern, handler):
        self._subscriptions.setdefault(pattern, []).append(handler)

    def registerCrypto(self, crypto):
        self._crypto = crypto

    def publish(self, topic, event, encrypt=False, serializer=None):
        # Backpressure enforcement based on attributes
        if self.queue_size is not None and len(self._queue) >= self.queue_size:
            if self.bp_policy == 'drop_oldest':
                # drop oldest, then allow enqueue
                if self._queue:
                    self._queue.pop(0)
            elif self.bp_policy == 'reject':
                # record dead letter and return False
                self.dead_letter_queue.append({'topic': topic, 'event': event})
                return False
            else:
                # default block policy raises exception
                raise Exception('Backpressure reject')
        # Handle encryption: decrypt and re-encrypt to simulate secure channel
        obj = event
        if encrypt and self._crypto:
            # JSON serialize for encryption
            s = json.dumps(event)
            enc = self._crypto.encrypt(s)
            dec = self._crypto.decrypt(enc)
            obj = json.loads(dec)
        # Serializer logic: use serialize()/deserialize() methods
        if serializer and serializer in self._serializers:
            ser = self._serializers[serializer]
            raw = ser.serialize(obj)
            obj = ser.deserialize(raw)
        # Backpressure handling
        # (handled above)
        # Enqueue event
        self._queue.append({'topic': topic, 'event': obj})
        return True

    def process(self):
        # Process all queued events
        while self._queue:
            rec = self._queue.pop(0)
            topic = rec['topic']
            event = rec['event']
            # Apply extensions to modify event
            for ext in self._extensions:
                try:
                    event = ext(event, topic)
                except Exception:
                    pass
            # Dispatch to matching handlers
            for pattern, handlers in self._subscriptions.items():
                if self._match(pattern, topic):
                    for h in handlers:
                        try:
                            h(topic, event)
                        except Exception as e:
                            self.dead_letter_queue.append({'topic': topic, 'error': str(e)})

    def registerSerializer(self, name, serializer):
        self._serializers[name] = serializer

    def batchPublish(self, topic, event):
        # Alias to publish for batch mode
        self.publish(topic, event)

    def updateConfigAtRuntime(self, key, value):
        # Update configuration and apply to attributes
        self.config[key] = value
        if key == 'queue_size':
            self.queue_size = value
        if key == 'backpressure_policy':
            self.bp_policy = value

    def registerExtension(self, ext):
        self._extensions.append(ext)

    def persistAndReplay(self, subscriber=None, file=None):
        # Persist events to file if file provided
        fn = file or self.config.get('persist_file')
        # Write current queue to file if persistence
        if fn:
            with open(fn, 'w') as f:
                for rec in self._queue:
                    f.write(json.dumps({'topic': rec['topic'], 'event': rec['event']}) + '\n')
        # Replay: read file or queue
        events = []
        if fn:
            with open(fn, 'r') as f:
                for line in f:
                    item = json.loads(line.strip())
                    events.append(item)
                    if subscriber:
                        subscriber(item['topic'], item['event'])
        return events

    def clusterDeploy(self, nodes):
        # Leader is smallest element
        if not nodes:
            leader = None
        else:
            leader = sorted(nodes)[0]
        self.leader = leader
        self.cluster_nodes = list(nodes)
        return leader

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