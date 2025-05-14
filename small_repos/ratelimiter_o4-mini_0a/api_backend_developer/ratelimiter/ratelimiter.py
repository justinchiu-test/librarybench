import datetime
import functools
import asyncio

def log_event(event_type, user_id, endpoint, decision, metadata=None):
    event = {
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user_id': user_id,
        'endpoint': endpoint,
        'decision': decision,
        'metadata': metadata or {}
    }
    return event

def chain_policies(*policies):
    def chained(user_id, endpoint):
        for policy in policies:
            res = policy(user_id, endpoint)
            if not isinstance(res, dict) or 'allowed' not in res:
                raise ValueError("Policy must return dict with 'allowed'")
            if not res['allowed']:
                return res
        return {'allowed': True, 'reason': 'all_policies_passed'}
    return chained

def validate_config(config):
    required = {'global_limit': int, 'burst_limit': int}
    for key, typ in required.items():
        if key not in config:
            raise ValueError(f"Missing config key: {key}")
        if not isinstance(config[key], typ):
            raise ValueError(f"Config key {key} must be {typ.__name__}")
    return True

def get_runtime_metrics(bucket_state):
    return {
        'tokens_used': bucket_state.get('tokens_used', 0),
        'tokens_left': bucket_state.get('tokens_left', 0),
        'next_refill': bucket_state.get('next_refill')
    }

def select_window_algo(algo_name):
    algos = {
        'sliding': 'sliding_window',
        'rolling': 'rolling_window',
        'fixed': 'fixed_window',
        'leaky': 'leaky_bucket'
    }
    if algo_name not in algos:
        raise ValueError("Unknown algorithm")
    return algos[algo_name]

class InProcessStore:
    def __init__(self):
        self.requests = {}

    def allow(self, user_id, endpoint):
        return True

def enable_fault_tolerant(store):
    try:
        available = store.is_available()
    except Exception:
        return InProcessStore()
    if not available:
        return InProcessStore()
    return store

def assign_priority_bucket(user_type):
    buckets = {'premium': 1, 'standard': 2, 'trial': 3}
    if user_type not in buckets:
        raise ValueError("Unknown user type")
    return buckets[user_type]

def persist_bucket_state(state, db):
    entry = state.copy()
    entry['timestamp'] = datetime.datetime.utcnow().isoformat()
    if 'state_history' not in db:
        db['state_history'] = []
    db['state_history'].append(entry)
    return True

def override_burst_capacity(base_capacity, override=None):
    return override if override is not None else base_capacity

def async_rate_limiter(limit=1):
    calls = {}
    def decorator(func):
        if not asyncio.iscoroutinefunction(func):
            raise ValueError("Function must be async")
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = func.__name__
            calls.setdefault(key, 0)
            if calls[key] >= limit:
                raise Exception("Rate limit exceeded")
            calls[key] += 1
            return await func(*args, **kwargs)
        return wrapper
    return decorator
