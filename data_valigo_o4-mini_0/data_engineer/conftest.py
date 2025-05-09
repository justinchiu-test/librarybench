import asyncio
import inspect
import pytest

def pytest_configure(config):
    # Register the asyncio marker so pytest doesn't warn about unknown marks
    config.addinivalue_line(
        "markers", "asyncio: mark test to be run as an asyncio coroutine"
    )

def pytest_collection_modifyitems(config, items):
    # Wrap any test function marked with @pytest.mark.asyncio
    for item in items:
        if item.get_closest_marker("asyncio"):
            func = item.obj
            if inspect.iscoroutinefunction(func):
                def _run_coroutine(*args, __func=func, **kwargs):
                    return asyncio.get_event_loop().run_until_complete(__func(*args, **kwargs))
                # replace the test function with our wrapper
                item.obj = _run_coroutine
