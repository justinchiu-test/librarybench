from concurrent.futures import ThreadPoolExecutor
import time
import collections

class ETLPipeline:
    def __init__(self):
        self.config = {
            'backpressure_threshold': 1000,
            'timeout': 30,
            'parallelism': 4
        }
        self.consumer_lag = 0
        self.thread_pool_usage = 0
        self.handler_counts = collections.Counter()
        self._executor = ThreadPoolExecutor(max_workers=self.config['parallelism'])
        self.serializer_registry = {}
        self.event_store = {'raw': [], 'processed': []}
        self.extension_registry = {}
        self.valid_tokens = set()
        self.dead_letter = []

    def reportHealth(self):
        return {
            'consumer_lag': self.consumer_lag,
            'thread_pool_usage': self.thread_pool_usage,
            'handler_counts': dict(self.handler_counts)
        }

    def balanceLoad(self, funcs_with_args):
        self.thread_pool_usage = self.config['parallelism']
        futures = []
        for func, args, kwargs in funcs_with_args:
            def wrapper(f, *a, **kw):
                result = f(*a, **kw)
                self.handler_counts[f.__name__] += 1
                return result
            future = self._executor.submit(wrapper, func, *args, **(kwargs or {}))
            futures.append(future)
        return futures

    def propagateContext(self, func, context):
        def wrapper(*args, **kwargs):
            merged = {'context': context, 'args': args, 'kwargs': kwargs}
            return func(merged)
        return wrapper

    def registerSerializer(self, name, serializer):
        self.serializer_registry[name] = serializer

    def persistEvents(self, raw_event, processed_event):
        self.event_store['raw'].append(raw_event)
        self.event_store['processed'].append(processed_event)

    def publishSync(self, events, process_func, serializer=None):
        for event in events:
            raw = event
            serialized = serializer.serialize(raw) if serializer else raw
            processed = process_func(raw)
            self.persistEvents(serialized, processed)

    def updateConfig(self, **kwargs):
        rebuild = False
        if 'parallelism' in kwargs and kwargs['parallelism'] != self.config['parallelism']:
            rebuild = True
        self.config.update(kwargs)
        if rebuild:
            self._executor.shutdown(wait=True)
            self._executor = ThreadPoolExecutor(max_workers=self.config['parallelism'])

    def registerExtension(self, name, extension):
        self.extension_registry[name] = extension

    def authenticate(self, token):
        return token in self.valid_tokens

    def addToken(self, token):
        self.valid_tokens.add(token)

    def handleErrors(self, func, retries=3, initial_delay=1):
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    time.sleep(delay)
                    delay *= 2
            error_event = {'func': func.__name__, 'args': args, 'kwargs': kwargs}
            self.dead_letter.append(error_event)
            raise
        return wrapper
