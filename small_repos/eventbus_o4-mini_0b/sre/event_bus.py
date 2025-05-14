import threading
import time
from concurrent.futures import ThreadPoolExecutor
import contextvars

class EventBus:
    def __init__(self, max_workers=5, retry_attempts=3):
        self.config = {
            'max_workers': max_workers,
            'retry_attempts': retry_attempts,
            'backoff_base': 0.1,
        }
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.subscribers = []  # list of (handler, token)
        self.serializers = {}  # name -> (encode, decode)
        self.persistent = False
        self.persistent_storage = []
        self._pending_tasks = 0
        self.extensions = []
        self.allowed_tokens = set()
        self.dead_letter = []
        self.context = contextvars.copy_context()

    def reportHealth(self):
        return {
            'thread_pool_size': self.config['max_workers'],
            'queue_depth': self._pending_tasks,
            'handler_count': len(self.subscribers),
        }

    def balanceLoad(self):
        # ThreadPoolExecutor handles load balancing.
        return True

    def propagateContext(self, func):
        # Decorator to propagate contextvars
        def wrapper(*args, **kwargs):
            ctx = contextvars.copy_context()
            return ctx.run(func, *args, **kwargs)
        return wrapper

    def registerSerializer(self, name, encode_func, decode_func):
        self.serializers[name] = (encode_func, decode_func)

    def persistEvents(self, enable=True):
        self.persistent = enable

    def publish(self, event, sync=False):
        token = event.get('token')
        self.authenticate(token)
        if self.persistent:
            self.persistent_storage.append(event)
        if sync:
            for handler, _ in self.subscribers:
                self._invoke_handler(handler, event)
        else:
            self._pending_tasks += 1
            def task():
                try:
                    for handler, _ in self.subscribers:
                        self._invoke_handler(handler, event)
                finally:
                    self._pending_tasks -= 1
            self.executor.submit(task)

    def publishSync(self, event):
        self.publish(event, sync=True)

    def updateConfig(self, **kwargs):
        # For thread pool size change, recreate executor if needed
        if 'max_workers' in kwargs and kwargs['max_workers'] != self.config['max_workers']:
            self.executor.shutdown(wait=False)
            self.executor = ThreadPoolExecutor(max_workers=kwargs['max_workers'])
        self.config.update(kwargs)

    def registerExtension(self, extension):
        self.extensions.append(extension)

    def authenticate(self, token):
        if token not in self.allowed_tokens:
            raise PermissionError("Unauthorized token")
        return True

    def addToken(self, token):
        self.allowed_tokens.add(token)

    def subscribe(self, handler, token=None):
        if token is None:
            raise ValueError("Token required for subscribing")
        self.authenticate(token)
        self.subscribers.append((handler, token))

    def handleErrors(self, handler):
        # returns a wrapped handler with retry and dead letter
        def wrapped(event):
            attempts = 0
            max_attempts = self.config.get('retry_attempts', 3)
            backoff_base = self.config.get('backoff_base', 0.1)
            while attempts < max_attempts:
                try:
                    return handler(event)
                except Exception:
                    attempts += 1
                    time.sleep(backoff_base * (2 ** (attempts - 1)))
            # dead letter
            self.dead_letter.append(event)
        return wrapped

    def _invoke_handler(self, handler, event):
        handler(event)

    def shutdown(self):
        self.executor.shutdown(wait=True)
