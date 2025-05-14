from contextlib import contextmanager

@contextmanager
def burst_override(bucket, extra_capacity):
    original = getattr(bucket, 'capacity', None)
    try:
        if hasattr(bucket, 'capacity'):
            bucket.capacity = original + extra_capacity
        yield bucket
    finally:
        if hasattr(bucket, 'capacity'):
            bucket.capacity = original
