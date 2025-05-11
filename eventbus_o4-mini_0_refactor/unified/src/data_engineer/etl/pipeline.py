import time
from concurrent.futures import ThreadPoolExecutor


class ETLPipeline:
    """
    Simple ETL pipeline for data engineering tests
    """
    def __init__(self):
        # Serializer and extension registries
        self.serializer_registry = {}
        self.extension_registry = {}
        # Event stores for raw and processed events
        self.event_store = {'raw': [], 'processed': []}
        # Configuration defaults
        self.config = {'parallelism': 1, 'timeout': None}
        # Thread pool executor and usage tracking
        self._executor = ThreadPoolExecutor(max_workers=self.config['parallelism'])
        self._executor_used = False
        # Authentication tokens
        self._tokens = set()
        # Dead letter list for failed events
        self.dead_letter = []
        # Handler invocation counts
        self._handler_counts = {}

    def reportHealth(self):
        return {
            'consumer_lag': 0,
            'thread_pool_usage': self.config['parallelism'] if self._executor_used else 0,
            'handler_counts': dict(self._handler_counts)
        }

    def registerSerializer(self, name, serializer):
        self.serializer_registry[name] = serializer

    def propagateContext(self, func, context):
        def wrapper(*args, **kwargs):
            merged = {'context': context, 'args': args, 'kwargs': kwargs}
            return func(merged)
        return wrapper

    def persistEvents(self, raw, processed):
        self.event_store.setdefault('raw', []).append(raw)
        self.event_store.setdefault('processed', []).append(processed)

    def publishSync(self, events, process, serializer=None):
        for e in events:
            try:
                raw = serializer.serialize(e) if serializer else e
            except Exception:
                # Skip failed serialization
                continue
            processed = process(e)
            self.persistEvents(raw, processed)

    def updateConfig(self, parallelism=None, timeout=None):
        if parallelism is not None:
            self.config['parallelism'] = parallelism
            # recreate executor
            self._executor = ThreadPoolExecutor(max_workers=parallelism)
        if timeout is not None:
            self.config['timeout'] = timeout

    def registerExtension(self, name, extension):
        self.extension_registry[name] = extension

    def addToken(self, token):
        self._tokens.add(token)

    def authenticate(self, token):
        return token in self._tokens

    def handleErrors(self, func, retries=1, initial_delay=1):
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    time.sleep(delay)
            # record to dead letter after retries
            entry = {'func': func.__name__, 'args': args, 'kwargs': kwargs}
            self.dead_letter.append(entry)
            # re-raise last exception
            raise last_exception
        return wrapper

    def _wrap_handler(self, func, args, kwargs):
        # count handler invocation
        name = getattr(func, '__name__', str(func))
        self._handler_counts[name] = self._handler_counts.get(name, 0) + 1
        return func(*args, **kwargs)

    def balanceLoad(self, tasks):
        # Submit tasks to thread pool and mark usage
        self._executor_used = True
        futures = []
        for func, args, kwargs in tasks:
            fut = self._executor.submit(self._wrap_handler, func, args, kwargs)
            futures.append(fut)
        return futures