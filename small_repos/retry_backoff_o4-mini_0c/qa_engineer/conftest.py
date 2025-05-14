import pytest
import asyncio
import inspect

def pytest_configure(config):
    # Register the asyncio marker so pytest won’t warn about unknown marks
    config.addinivalue_line(
        "markers",
        "asyncio: mark test to run under an asyncio event loop (via anyio)",
    )

def pytest_collection_modifyitems(config, items):
    """
    Convert pytest.mark.asyncio into pytest.mark.anyio so that async tests
    decorated with @pytest.mark.asyncio will be executed by the AnyIO plugin
    instead of being skipped.
    """
    for item in items:
        if item.get_closest_marker("asyncio"):
            item.add_marker(pytest.mark.anyio)

def pytest_pyfunc_call(pyfuncitem):
    """
    Hook to execute async def test functions by running them on the event loop.
    This ensures async tests are not skipped even if no async plugin is installed.
    """
    test_func = pyfuncitem.obj
    if inspect.iscoroutinefunction(test_func):
        # Get or create an event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        # Run the coroutine test
        loop.run_until_complete(test_func(**pyfuncitem.funcargs))
        return True
    # For non-async tests, let pytest handle them normally
    return None
