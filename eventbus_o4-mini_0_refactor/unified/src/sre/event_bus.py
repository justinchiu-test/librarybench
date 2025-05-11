"""
SRE Engineer EventBus implementation
"""
import contextvars
from concurrent.futures import ThreadPoolExecutor


class EventBus:
    def __init__(self, max_workers=1, retry_attempts=1):
        # Thread pool for async publishes
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        # Authentication tokens
        self._tokens = set()
        # Subscribers
        self._subscribers = []
        # Retry settings
        self.retry_attempts = retry_attempts
        # Dead-letter storage
        self.dead_letter = []
        # Persistence
        self._persistence_enabled = False
        self.persistent_storage = []
        # Extensions
        self.extensions = []
        # Configuration
        self.config = {'retry_attempts': retry_attempts}

    def addToken(self, token):
        self._tokens.add(token)

    def subscribe(self, handler, token=None):
        if token not in self._tokens:
            raise PermissionError('Invalid token')
        self._subscribers.append(handler)

    def publish(self, event, sync=True):
        # Authentication
        token = event.get('token')
        if token not in self._tokens:
            raise PermissionError('Invalid token')
        # Persistence
        if self._persistence_enabled:
            self.persistent_storage.append(event)
        # Dispatch
        if sync:
            for h in self._subscribers:
                h(event)
        else:
            for h in self._subscribers:
                self._executor.submit(h, event)

    def publishSync(self, event):
        return self.publish(event, sync=True)

    def shutdown(self):
        self._executor.shutdown(wait=True)

    def persistEvents(self, enabled):
        self._persistence_enabled = enabled

    def reportHealth(self):
        return {
            'thread_pool_size': getattr(self._executor, '_max_workers', None),
            'queue_depth': 0,
            'handler_count': len(self._subscribers)
        }

    def registerSerializer(self, name, enc_fn, dec_fn):
        self.serializers = getattr(self, 'serializers', {})
        self.serializers[name] = (enc_fn, dec_fn)

    def updateConfig(self, **kwargs):
        from concurrent.futures import ThreadPoolExecutor
        for k, v in kwargs.items():
            self.config[k] = v
            if k == 'max_workers':
                # reconfigure thread pool
                self._executor = ThreadPoolExecutor(max_workers=v)
            elif k == 'retry_attempts':
                self.retry_attempts = v

    def balanceLoad(self):
        return True

    def propagateContext(self, func):
        def wrapper(*args, **kwargs):
            ctx = contextvars.copy_context()
            return ctx.run(func, *args, **kwargs)
        return wrapper

    def handleErrors(self, func):
        def wrapper(event):
            exception_occurred = False
            last_exc = None
            for _ in range(self.retry_attempts):
                try:
                    return func(event)
                except Exception as e:
                    exception_occurred = True
                    last_exc = e
                    continue
            # poison event after all retries
            if exception_occurred:
                self.dead_letter.append(event)
            return None
        return wrapper

    def getConfig(self):
        return dict(self.config)

    def registerExtension(self, ext):
        self.extensions.append(ext)