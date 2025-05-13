import pytest
import inspect
import asyncio

def pytest_configure(config):
    # Declare the "asyncio" marker so we don't get unknown-marker warnings.
    config.addinivalue_line(
        "markers",
        "asyncio: mark test to be run with an asyncio event loop"
    )

def pytest_collection_modifyitems(config, items):
    """
    Any test that's either an async def or marked @pytest.mark.asyncio
    should also be marked @pytest.mark.anyio so that the anyio plugin picks it up.
    """
    for item in items:
        is_async_func = inspect.iscoroutinefunction(getattr(item, "obj", None))
        has_asyncio_mark = item.get_closest_marker("asyncio") is not None
        if is_async_func or has_asyncio_mark:
            item.add_marker("anyio")

def pytest_pyfunc_call(pyfuncitem):
    """
    Run async test functions in an event loop if they are coroutine functions.
    """
    test_func = getattr(pyfuncitem, "obj", None)
    if inspect.iscoroutinefunction(test_func):
        # Run the async test function with pytest's funcargs
        asyncio.run(test_func(**pyfuncitem.funcargs))
        return True  # Skip the default call handling
    # For non-async tests, fall back to the default runner
    return None
