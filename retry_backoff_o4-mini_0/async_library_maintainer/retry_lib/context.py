import asyncio
import contextvars

# Ensure there is a running event loop by default on import (for run_until_complete calls).
# In Python 3.10+ get_event_loop() raises if no loop is set; so we auto-create one.
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

_retry_context_var = contextvars.ContextVar('retry_context', default={})

def set_context(key, value):
    ctx = _retry_context_var.get().copy()
    ctx[key] = value
    _retry_context_var.set(ctx)

def get_context(key, default=None):
    return _retry_context_var.get().get(key, default)

def get_all_context():
    return _retry_context_var.get()

def clear_context():
    _retry_context_var.set({})
