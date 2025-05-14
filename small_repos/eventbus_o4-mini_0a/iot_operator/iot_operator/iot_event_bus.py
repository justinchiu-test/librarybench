import threading
import queue
import json
import os
import glob
import uuid
from collections import deque

class Serializer:
    def dumps(self, obj):
        raise NotImplementedError

    def loads(self, data):
        raise NotImplementedError

class JsonSerializer(Serializer):
    def dumps(self, obj):
        return json.dumps(obj).encode('utf-8')

    def loads(self, data):
        return json.loads(data.decode('utf-8'))

class EventBus:
    def __init__(self):
        self._subscriptions = []  # list of (pattern, callback)
        self._dead_letter_queue = []
        self._crypto_module = None
        self._backpressure_policy = 'block'
        self._queue_limit = 1000
        self._queue = queue.Queue(maxsize=self._queue_limit)
        self._serializers = {'json': JsonSerializer()}
        self._extensions = []
        self._config = {}
        self._cluster_deployed = False
        self._persist_dir = 'event_persist'
        os.makedirs(self._persist_dir, exist_ok=True)
        self._lock = threading.RLock()

    # Wildcard matching
    def _match(self, pattern, topic):
        pat_parts = pattern.split('/')
        topic_parts = topic.split('/')
        i = j = 0
        while i < len(pat_parts) and j < len(topic_parts):
            if pat_parts[i] == '#':
                return True
            if pat_parts[i] == '*':
                i += 1
                j += 1
                continue
            if pat_parts[i] != topic_parts[j]:
                return False
            i += 1
            j += 1
        if i == len(pat_parts) and j == len(topic_parts):
            return True
        if i == len(pat_parts)-1 and pat_parts[i] == '#':
            return True
        return False

    def subscribeWildcard(self, pattern, callback):
        with self._lock:
            self._subscriptions.append((pattern, callback))

    def routeToDeadLetterQueue(self, topic, message):
        self._dead_letter_queue.append((topic, message))

    def getDeadLetterQueue(self):
        return list(self._dead_letter_queue)

    def encryptEvent(self, crypto_module):
        self._crypto_module = crypto_module

    def applyBackpressure(self, policy, queue_limit=None):
        with self._lock:
            if queue_limit:
                self._queue_limit = queue_limit
                self._queue = queue.Queue(maxsize=self._queue_limit)
            self._backpressure_policy = policy

    def registerSerializer(self, name, serializer):
        self._serializers[name] = serializer

    def batchPublish(self, topic, messages, serializer='json'):
        for msg in messages:
            self.publish(topic, msg, serializer=serializer)

    def updateConfigAtRuntime(self, config_updates):
        with self._lock:
            self._config.update(config_updates)
            # apply known configs
            if 'backpressure_policy' in config_updates:
                self.applyBackpressure(config_updates['backpressure_policy'])
            if 'queue_limit' in config_updates:
                # apply queue_limit with current policy
                self.applyBackpressure(self._backpressure_policy, config_updates['queue_limit'])

    def clusterDeploy(self, config=None):
        self._cluster_deployed = True

    def persistAndReplay(self, topic, message=None):
        if message is not None:
            fname = os.path.join(self._persist_dir, f"{uuid.uuid4()}.evt")
            with open(fname, 'wb') as f:
                data = json.dumps({'topic': topic, 'message': message}).encode('utf-8')
                f.write(data)
        else:
            events = []
            files = glob.glob(os.path.join(self._persist_dir, '*.evt'))
            for fname in files:
                with open(fname, 'rb') as f:
                    data = json.loads(f.read().decode('utf-8'))
                    events.append(data)
            return events

    def registerExtension(self, extension_callback):
        self._extensions.append(extension_callback)

    def publish(self, topic, message, serializer='json'):
        # serialize
        if serializer not in self._serializers:
            raise ValueError("Unknown serializer")
        data = self._serializers[serializer].dumps(message)
        # encrypt
        if self._crypto_module:
            data = self._crypto_module.encrypt(data)
        # backpressure
        dropped = False
        try:
            if self._backpressure_policy == 'block':
                self._queue.put((topic, data), block=True)
            elif self._backpressure_policy == 'drop_oldest':
                if self._queue.full():
                    try:
                        self._queue.get_nowait()
                        dropped = True
                    except queue.Empty:
                        pass
                self._queue.put((topic, data), block=False)
            elif self._backpressure_policy == 'reject':
                self._queue.put((topic, data), block=False)
            else:
                self._queue.put((topic, data), block=True)
        except queue.Full:
            # reject policy full
            raise RuntimeError("Backpressure queue is full")

        # persist
        self.persistAndReplay(topic, message)

        # dispatch logic:
        # - block always dispatches immediately
        # - drop_oldest dispatches only when an old message was dropped
        # - reject does NOT dispatch automatically
        if self._backpressure_policy == 'block':
            self._dispatch()
        elif self._backpressure_policy == 'drop_oldest':
            if dropped:
                self._dispatch()
        elif self._backpressure_policy == 'reject':
            # do not dispatch automatically for reject policy
            pass
        else:
            # unknown policies default to dispatch
            self._dispatch()

    def _dispatch(self):
        while not self._queue.empty():
            topic, data = self._queue.get()
            # decrypt
            if self._crypto_module:
                try:
                    payload = self._crypto_module.decrypt(data)
                except Exception:
                    self.routeToDeadLetterQueue(topic, data)
                    continue
            else:
                payload = data
            # deserialize
            deserialized = None
            for name, ser in self._serializers.items():
                try:
                    deserialized = ser.loads(payload)
                    break
                except Exception:
                    continue
            if deserialized is None:
                self.routeToDeadLetterQueue(topic, payload)
                continue
            # extensions
            for ext in self._extensions:
                try:
                    ext(topic, deserialized)
                except Exception:
                    self.routeToDeadLetterQueue(topic, deserialized)
            # subscriptions
            for pattern, callback in list(self._subscriptions):
                if self._match(pattern, topic):
                    try:
                        callback(topic, deserialized)
                    except Exception:
                        self.routeToDeadLetterQueue(topic, deserialized)
