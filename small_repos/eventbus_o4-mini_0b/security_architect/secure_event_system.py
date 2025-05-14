import threading
import time
import random
import hmac
import hashlib

class SecureEventSystem:
    def __init__(self):
        self._current_user = None
        self._lock = threading.Lock()
        self._workers = []
        self._worker_index = 0
        self._context = threading.local()
        self._serializers = {}
        self._events = {}  # tenant -> list of (event, signature)
        self._handlers = []
        self._config = {}
        self._extensions = {}
        self._logs = []
        self._quarantine = []

    def authenticate(self, token):
        # simple token is dict with 'user' and 'roles'
        if not isinstance(token, dict) or 'user' not in token or 'roles' not in token:
            raise ValueError("Invalid token")
        self._current_user = token
        return True

    def reportHealth(self):
        if not self._current_user or 'admin' not in self._current_user.get('roles', []):
            raise PermissionError("Access denied")
        return {
            'threads': threading.active_count(),
            'queues': 0,
            'handlers': len(self._handlers)
        }

    def balanceLoad(self, task, *args, **kwargs):
        with self._lock:
            if not self._workers:
                self._workers.append(threading.current_thread())
            idx = self._worker_index % len(self._workers)
            self._worker_index += 1
        return task(*args, **kwargs)

    def propagateContext(self, **context):
        if not hasattr(self._context, 'data'):
            self._context.data = {}
        self._context.data.update(context)

    def getContext(self):
        return getattr(self._context, 'data', {}).copy()

    def registerSerializer(self, name, serializer, deserializer):
        self._serializers[name] = (serializer, deserializer)

    def serialize(self, name, obj):
        if name not in self._serializers:
            raise KeyError("Serializer not found")
        ser, _ = self._serializers[name]
        return ser(obj)

    def deserialize(self, name, data):
        if name not in self._serializers:
            raise KeyError("Serializer not found")
        _, des = self._serializers[name]
        return des(data)

    def persistEvents(self, tenant, event):
        key = self.getContext().get('key', b'')
        payload = repr(event).encode()
        sig = hmac.new(key, payload, hashlib.sha256).hexdigest()
        self._events.setdefault(tenant, []).append((event, sig))
        return True

    def verifyEvents(self, tenant):
        key = self.getContext().get('key', b'')
        for event, sig in self._events.get(tenant, []):
            expected = hmac.new(key, repr(event).encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(expected, sig):
                return False
        return True

    def publishSync(self, event):
        results = []
        for handler in self._handlers:
            results.append(handler(event))
        return results

    def registerHandler(self, handler):
        self._handlers.append(handler)

    def updateConfig(self, **kwargs):
        self._config.update(kwargs)

    def getConfig(self):
        return self._config.copy()

    def registerExtension(self, name, extension):
        self._extensions[name] = extension

    def getExtension(self, name):
        return self._extensions.get(name)

    def handleErrors(self, func):
        def wrapper(event):
            retries = 3
            for attempt in range(retries):
                try:
                    return func(event)
                except Exception as e:
                    self._logs.append(str(e))
                    time.sleep(random.random() * 0.01)
            self._quarantine.append(event)
            return None
        return wrapper

    def getLogs(self):
        return list(self._logs)

    def getQuarantine(self):
        return list(self._quarantine)
