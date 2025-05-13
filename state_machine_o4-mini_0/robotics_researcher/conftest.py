import pytest
import asyncio
import inspect

# Provide a simple pytest.mark.asyncio decorator that runs async tests via asyncio.run
def _asyncio_mark(func):
    if inspect.iscoroutinefunction(func):
        def wrapper(*args, **kwargs):
            return asyncio.run(func(*args, **kwargs))
        # Preserve metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return func

# Override/define pytest.mark.asyncio so async tests are collected as normal sync tests
pytest.mark.asyncio = _asyncio_mark

def pytest_configure(config):
    # Register the "asyncio" marker to avoid warnings
    config.addinivalue_line(
        "markers",
        "asyncio: mark test to run as asyncio via the anyio plugin"
    )

def pytest_collection_modifyitems(session, config, items):
    """
    Keep the original logic: tests marked 'asyncio' also get marked 'anyio'
    so anyio-based fixtures would still work if present.
    """
    for item in items:
        if any(mark.name == "asyncio" for mark in item.iter_markers()):
            item.add_marker(pytest.mark.anyio)
