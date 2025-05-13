import time
import functools

def fallback_reads(data, context):
    return [{'id': 'dummy', 'seq': 'N', 'chr': '', 'pos': 0, 'gene': '', 'quality': 0, 'mismatches': 0}]

def skip_reads(reads, threshold, context):
    kept = []
    skipped = 0
    for r in reads:
        if r.get('mismatches', 0) > threshold:
            skipped += 1
        else:
            kept.append(r)
    context['metrics'].inc('skipped_reads', skipped)
    return kept

def retry(max_retries=3, backoff_factor=0.1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if retries >= max_retries:
                        raise
                    time.sleep(backoff_factor * (2 ** retries))
                    retries += 1
        return wrapper
    return decorator
