import sys
import json
import inspect
from .registry import register_renderer, register_task, register_workflow_step
from .i18n import translate_text
from .io_redirector import redirect_io
import os

def set_renderer(name):
    def deco(func):
        register_renderer(name, func)
        return func
    return deco

def pipe(func):
    def wrapper(*args, **kwargs):
        if not args and sys.stdin and not sys.stdin.isatty():
            data = sys.stdin.read()
            try:
                parsed = json.loads(data)
            except Exception:
                parsed = data
            return func(parsed, **kwargs)
        return func(*args, **kwargs)
    return wrapper

def parallelize(func):
    func.parallelizable = True
    register_task(func.__name__, func)
    return func

def secure(func):
    # placeholder if needed
    return func

def translate(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if isinstance(result, str):
            return translate_text(result)
        return result
    return wrapper

def export_workflow(func):
    register_workflow_step(func)
    return func

def env_inject(func):
    sig = inspect.signature(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind_partial(*args, **kwargs)
        for name, param in sig.parameters.items():
            if name not in bound.arguments:
                env_key = name.upper()
                if env_key in os.environ:
                    bound.arguments[name] = os.environ[env_key]
        return func(*bound.args, **bound.kwargs)
    return wrapper

def redirect(func=None, *, stdin=None, stdout=None, stderr=None):
    def deco(f):
        def wrapper(*args, **kwargs):
            with redirect_io(stdin=stdin, stdout=stdout, stderr=stderr):
                return f(*args, **kwargs)
        return wrapper
    if func:
        return deco(func)
    return deco
