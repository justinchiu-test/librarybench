import threading
import time

class Event:
    def __init__(self, id, payload, routing_key):
        self.id = id
        self.payload = payload
        self.routing_key = routing_key

class EventBus:
    def __init__(self):
        self.subscribers = []  # list of (pattern, callback)
        self.dead_letter_queue = []
        self.crypto_module = None
        self.backpressure_policy = 'reject'  # 'block', 'drop_oldest', 'reject'
        self.backpressure_limit = 100
        self.queue = []
        self.serializers = {}
        self.config = {}
        self.cluster = {'nodes': [], 'leader': None, 'replicated_stores': {}}
        self.persistent_store = []
        self.extensions = []
        self.lock = threading.Lock()

    def subscribeWildcard(self, pattern, callback):
        self.subscribers.append((pattern, callback))

    def _match(self, routing_key, pattern):
        rk_tokens = routing_key.split('.')
        p_tokens = pattern.split('.')
        i = j = 0
        while i < len(rk_tokens) and j < len(p_tokens):
            p = p_tokens[j]
            if p == '#':
                return True
            if p == '*':
                i += 1
                j += 1
                continue
            if rk_tokens[i] != p:
                return False
            i += 1
            j += 1
        if i == len(rk_tokens) and j == len(p_tokens):
            return True
        if j < len(p_tokens) and p_tokens[j] == '#':
            return True
        return False

    def routeToDeadLetterQueue(self, event, reason=None):
        entry = {'event': event, 'reason': reason}
        self.dead_letter_queue.append(entry)

    def registerCryptoModule(self, module):
        self.crypto_module = module

    def applyBackpressure(self, limit, policy):
        self.backpressure_limit = limit
        self.backpressure_policy = policy

    def registerSerializer(self, name, serializer):
        self.serializers[name] = serializer

    def batchPublish(self, events):
        for ev in events:
            self.publish(ev, ev.routing_key)

    def updateConfigAtRuntime(self, **kwargs):
        for k, v in kwargs.items():
            if k == 'backpressure_limit':
                self.backpressure_limit = v
            elif k == 'backpressure_policy':
                self.backpressure_policy = v
            else:
                self.config[k] = v

    def clusterDeploy(self, nodes):
        self.cluster['nodes'] = list(nodes)
        if nodes:
            self.cluster['leader'] = nodes[0]
        # replicate current persistent store
        replicated = {}
        for node in nodes:
            replicated[node] = list(self.persistent_store)
        self.cluster['replicated_stores'] = replicated

    def persistAndReplay(self, start_index=0):
        return list(self.persistent_store[start_index:])

    def registerExtension(self, extension_fn):
        self.extensions.append(extension_fn)

    def serialize(self, name, event):
        if name not in self.serializers:
            raise ValueError("Serializer not found")
        return self.serializers[name].serialize(event)

    def publish(self, event, routing_key):
        # missing fields
        if not hasattr(event, 'payload') or event.payload is None:
            self.routeToDeadLetterQueue(event, reason='missing_payload')
            return
        if not routing_key:
            self.routeToDeadLetterQueue(event, reason='missing_routing_key')
            return
        # encrypt
        if self.crypto_module:
            try:
                event.payload = self.crypto_module.encrypt(event.payload)
            except Exception as e:
                self.routeToDeadLetterQueue(event, reason='encryption_error')
                return
        # persist
        self.persistent_store.append(event)
        # apply extensions
        for ext in list(self.extensions):
            try:
                ev2 = ext(event)
                if ev2 is None:
                    return
                event = ev2
            except Exception as e:
                self.routeToDeadLetterQueue(event, reason='extension_error')
                return
        # dispatch to subscribers
        for pattern, callback in list(self.subscribers):
            if self._match(routing_key, pattern):
                try:
                    callback(event)
                except Exception as e:
                    self.routeToDeadLetterQueue(event, reason='handler_exception')
        # backpressure queue
        with self.lock:
            if len(self.queue) >= self.backpressure_limit:
                if self.backpressure_policy == 'block':
                    # simple blocking
                    while len(self.queue) >= self.backpressure_limit:
                        time.sleep(0.01)
                    self.queue.append(event)
                elif self.backpressure_policy == 'drop_oldest':
                    self.queue.pop(0)
                    self.queue.append(event)
                elif self.backpressure_policy == 'reject':
                    # reject new event
                    return
            else:
                self.queue.append(event)
