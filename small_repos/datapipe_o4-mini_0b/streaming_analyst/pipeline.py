import json
import time
from functools import wraps

class Counter:
    def __init__(self, name):
        self.name = name
        self.count = 0

    def increment(self, amount=1):
        self.count += amount

    @property
    def value(self):
        return self.count

class StreamingPipeline:
    def __init__(self):
        self.streaming_enabled = False
        self.skip_on_error = False
        self.rate_limit = None
        self.exporter_started = False
        self.counters = {}

    def enable_streaming(self):
        self.streaming_enabled = True

    def set_skip_on_error(self):
        self.skip_on_error = True

    def set_rate_limit(self, limit):
        self.rate_limit = limit

    def start_prometheus_exporter(self):
        self.exporter_started = True

    def create_counter(self, name):
        counter = Counter(name)
        self.counters[name] = counter
        return counter

    def get_counters(self):
        return {name: c.value for name, c in self.counters.items()}

def scaffold_pipeline(pipeline_name='pipeline'):
    """
    Returns a JSON scaffold for a new pipeline.
    """
    scaffold = {
        "pipeline_name": pipeline_name,
        "transforms": [],
        "sources": [],
        "sinks": []
    }
    return json.dumps(scaffold)

def run_pipeline(stream=False):
    """
    Returns a StreamingPipeline instance for streaming execution.
    """
    if stream:
        p = StreamingPipeline()
        # ensure streaming flag matches requested mode
        p.enable_streaming()
        return p
    else:
        raise ValueError("Only streaming mode is supported in this stub")

def monitor_pipeline(pipeline):
    """
    Returns current counters as a dict.
    """
    if not isinstance(pipeline, StreamingPipeline):
        raise TypeError("Expected a StreamingPipeline instance")
    return pipeline.get_counters()

def debug_pipeline(func, record):
    """
    Runs func(record); on exception returns debug info.
    """
    try:
        return func(record)
    except Exception as e:
        return {"error": str(e), "record": record}

def enable_streaming(pipeline):
    pipeline.enable_streaming()
    return pipeline

def set_skip_on_error(pipeline):
    pipeline.set_skip_on_error()
    return pipeline

def create_counter(name):
    return Counter(name)

def set_rate_limit(pipeline, limit):
    pipeline.set_rate_limit(limit)
    return pipeline

def start_prometheus_exporter(pipeline):
    pipeline.start_prometheus_exporter()
    return pipeline

class Processor:
    """
    Base class for stateful transforms.
    """
    def __init__(self):
        pass

    def process(self, record):
        """
        Override this method in subclasses.
        """
        raise NotImplementedError("Processor.process must be implemented by subclasses")

def validate_schema(record, schema):
    """
    Simple JSON Schema validation: checks required keys.
    """
    required = schema.get("required", [])
    missing = [key for key in required if key not in record]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
    return True

def retry_on_error(retries=3, backoff_factor=0.1):
    """
    Decorator to retry transient failures.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    # simulate backoff without actual sleep for stub
                    continue
            raise last_exc
        # Prevent pytest from collecting decorated funcs as tests
        wrapper.__test__ = False
        return wrapper
    return decorator

def halt_on_error(func):
    """
    Decorator to fail fast on error.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    # Prevent pytest from collecting decorated funcs as tests
    wrapper.__test__ = False
    return wrapper
