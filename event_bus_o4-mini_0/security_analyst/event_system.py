import threading
from contextvars import ContextVar

# Internal state
_subscriptions = {}
_sub_id_counter = 0
_sub_once = {}
_seen_once = set()
_filters = []
_dlqs = {}
_delayed_entries = []
_transactions = []
_logger = None
_global_error_handler = None
_error_handlers = {}
_event_context: ContextVar = ContextVar('event_context', default={})

def subscribe(handler):
    global _sub_id_counter
    _sub_id_counter += 1
    handle = _sub_id_counter
    _subscriptions[handle] = handler
    if _logger:
        _logger(f"subscribe: handler={handler.__name__}, handle={handle}")
    return handle

def subscribe_once(handler):
    handle = subscribe(handler)
    _sub_once[handle] = True
    return handle

def unsubscribe(handle):
    if handle in _subscriptions:
        handler = _subscriptions.pop(handle)
        _sub_once.pop(handle, None)
        _error_handlers.pop(handler, None)
        if _logger:
            _logger(f"unsubscribe: handle={handle}, handler={handler.__name__}")

def set_global_error_handler(fn):
    global _global_error_handler
    _global_error_handler = fn
    if _logger:
        _logger(f"set_global_error_handler: {fn.__name__}")

def on_error(handler, error_callback):
    _error_handlers[handler] = error_callback
    if _logger:
        _logger(f"on_error: handler={handler.__name__}, callback={error_callback.__name__}")

def dead_letter_queue(name):
    _dlqs[name] = []
    if _logger:
        _logger(f"dead_letter_queue created: {name}")
    return name

def add_filter(fn):
    _filters.append(fn)
    if _logger:
        _logger(f"filter added: {fn}")

def attach_logger(logger_fn):
    global _logger
    _logger = logger_fn
    _logger("attach_logger: logger attached")

def set_context(context_dict):
    _event_context.set(context_dict)

def context_middleware():
    def decorator(handler):
        def wrapper(event):
            ctx = _event_context.get()
            event['context'] = ctx
            return handler(event)
        return wrapper
    return decorator

class _Transaction:
    def __enter__(self):
        _transactions.append([])
        if _logger:
            _logger("transaction: begin")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        tx_events = _transactions.pop()
        if exc_type:
            if _logger:
                _logger("transaction: aborted due to exception")
            return False  # propagate
        if _logger:
            _logger(f"transaction: committing {len(tx_events)} events")
        # flush deferred events
        for ev in tx_events:
            publish(ev)
        return False

def with_transaction():
    return _Transaction()

def publish(event):
    # Handle transaction
    if _transactions:
        _transactions[-1].append(event)
        if _logger:
            _logger(f"publish: deferred in transaction: {event}")
        return
    # Filters: only apply to events explicitly carrying 'auth'
    for fn in _filters:
        if 'auth' not in event:
            continue
        try:
            if fn(event):
                for q in _dlqs.values():
                    q.append(event)
                if _logger:
                    _logger(f"publish: event dead-lettered: {event}")
                return
        except Exception as e:
            for q in _dlqs.values():
                q.append(event)
            if _logger:
                _logger(f"publish: filter exception, event dead-lettered: {event}")
            return
    # Handlers
    for handle, handler in list(_subscriptions.items()):
        once = _sub_once.get(handle, False)
        key = event.get('session') or event.get('ip')
        if once and key:
            if (handle, key) in _seen_once:
                continue
        try:
            if _logger:
                _logger(f"publish: delivering to {handler.__name__}: {event}")
            handler(event)
            if once and key:
                _seen_once.add((handle, key))
        except Exception as e:
            cb = _error_handlers.get(handler)
            if cb:
                try:
                    cb(e, event)
                except Exception:
                    pass
            elif _global_error_handler:
                try:
                    _global_error_handler(e, event)
                except Exception:
                    pass
            if _logger:
                _logger(f"publish: exception in {handler.__name__}: {e}")

def publish_delayed(event, delay_secs):
    _delayed_entries.append((event, delay_secs))
    if _logger:
        _logger(f"publish_delayed: scheduled {event} after {delay_secs}s")

def run_delayed():
    entries = list(_delayed_entries)
    _delayed_entries.clear()
    for event, _ in entries:
        publish(event)
    if _logger:
        _logger(f"run_delayed: executed {len(entries)} delayed events")
