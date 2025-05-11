"""
Secure Event System for Security Architect domain
"""
import threading


class SecureEventSystem:
    def __init__(self):
        # Thread-local context for authentication and propagation
        self._local = threading.local()
        # Handlers list
        self._handlers = []
        # Logs for error handling
        self._logs = []
        # Quarantined events on failure
        self._quarantine = []
        # Configuration store
        self._config = {}

    def authenticate(self, token):
        # Store token in thread-local; only admin role allowed
        self._local.token = token

    def reportHealth(self):
        # Only allow admin role
        token = getattr(self._local, 'token', None)
        if not token or 'admin' not in token.get('roles', []):
            raise PermissionError('Not authorized')
        # return dummy health data
        return {'threads': 0, 'handlers': len(self._handlers)}

    def balanceLoad(self, func, arg):
        # Simply invoke function
        return func(arg)

    def propagateContext(self, **kwargs):
        # Set context values in thread-local storage
        for k, v in kwargs.items():
            setattr(self._local, k, v)

    def getContext(self):
        # Return current thread-local context as dict
        return {k: v for k, v in vars(self._local).items() if k != 'token'}

    def registerSerializer(self, name, enc_fn, dec_fn):
        # Serializer registry: name -> (enc, dec)
        self._serializers = getattr(self, '_serializers', {})
        self._serializers[name] = (enc_fn, dec_fn)

    def serialize(self, name, data):
        if name not in getattr(self, '_serializers', {}):
            raise KeyError(f"Serializer '{name}' not found")
        enc, _ = self._serializers[name]
        return enc(data)

    def deserialize(self, name, data):
        if name not in getattr(self, '_serializers', {}):
            raise KeyError(f"Serializer '{name}' not found")
        _, dec = self._serializers[name]
        return dec(data)

    def persistEvents(self, topic, event):
        # Store events with signature for tamper detection
        # Initialize event store
        self._events = getattr(self, '_events', {})
        store = self._events.setdefault(topic, [])
        # Compute simple signature based on context key
        key = getattr(self._local, 'key', None)
        raw = repr(event).encode('utf-8')
        sig = self._sign(raw, key) if key else None
        store.append((event, sig))

    def _sign(self, data, key):
        # Simple signature: XOR bytes
        if not key:
            return None
        return bytes([b ^ key[0] for b in data])

    def verifyEvents(self, topic):
        # Verify stored events match signatures
        store = getattr(self, '_events', {}).get(topic, [])
        key = getattr(self._local, 'key', None)
        for event, sig in store:
            if sig is None:
                return False
            raw = repr(event).encode('utf-8')
            if self._sign(raw, key) != sig:
                return False
        return True

    def registerHandler(self, handler):
        self._handlers.append(handler)

    def publishSync(self, event):
        # Invoke all handlers in registration order
        results = []
        for h in self._handlers:
            results.append(h(event))
        return results

    def updateConfig(self, **kwargs):
        self._config.update(kwargs)

    def getConfig(self):
        return dict(self._config)

    def registerExtension(self, name, ext):
        self._extensions = getattr(self, '_extensions', {})
        self._extensions[name] = ext

    def getExtension(self, name):
        return getattr(self, '_extensions', {}).get(name)

    def handleErrors(self, func):
        # Decorator for error handling with retries and quarantine
        def wrapper(event):
            retries = self._config.get('retries', 3)
            count = 0
            while count < retries:
                try:
                    return func(event)
                except Exception as e:
                    self._logs.append(str(e))
                    count += 1
            # quarantine after retries
            self._quarantine.append(event)
            return None
        return wrapper

    def getQuarantine(self):
        return list(self._quarantine)

    def getLogs(self):
        return list(self._logs)