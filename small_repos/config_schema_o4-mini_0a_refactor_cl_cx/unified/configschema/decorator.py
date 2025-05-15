"""
Decorator for binding configuration values to function parameters.
"""
import inspect
import functools
from .config import ConfigManager

def with_config(arg=None):
    """
    Decorator to inject ConfigManager into functions.
    Usage:
      @with_config(path)
      def func(...)
    or:
      @with_config
      def func(cfg, ...)
    """
    # No argument decorator
    if callable(arg) and not isinstance(arg, str):  # used as @with_config
        func = arg
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not args:
                raise ValueError("Configuration path not provided")
            path = args[0]
            mgr = ConfigManager(path)
            return func(mgr, *args[1:], **kwargs)
        return wrapper

    # Decorator with path argument
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            mgr = ConfigManager(arg)
            sig = inspect.signature(func)
            bound = {}
            for name, param in sig.parameters.items():
                # inject config manager for parameter named 'config'
                if name == 'config':
                    bound[name] = mgr
                    continue
                # skip instance reference for methods
                if name == 'self':
                    continue
                # Skip if argument supplied explicitly
                if name in kwargs:
                    bound[name] = kwargs[name]
                    continue
                # For defaults
                if param.default is not inspect._empty:
                    bound[name] = param.default
                    continue
                # Required parameters: fetch from config
                annotation = param.annotation
                try:
                    val = mgr.get(name)
                except KeyError:
                    # Prompt if no default
                    val = mgr.get(name, prompt_missing=True)
                # Cast to annotation if provided
                if annotation is not inspect._empty:
                    try:
                        if not isinstance(val, annotation):
                            val = annotation(val)
                    except Exception:
                        pass
                bound[name] = val
            # Call method or function with appropriate 'self' if needed
            params = list(sig.parameters)
            # If method (first param 'self') and instance provided in args
            if params and params[0] == 'self' and args:
                return func(args[0], **bound)
            return func(**bound)
        return wrapper
    return decorator