import asyncio
import pytest

@pytest.fixture(autouse=True)
def ensure_event_loop():
    """
    Make sure there's always an asyncio event loop set in the main thread,
    so that tests calling asyncio.get_event_loop().run_until_complete(...) just work.
    """
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    yield

def pytest_collection_modifyitems(config, items):
    """
    Deselect any tests parametrized with [trio], since trio isn't installed.
    We'll only keep the asyncio backend runs.
    """
    deselected = []
    kept = []
    for item in items:
        # nodeid contains backend name in square brackets, e.g. "...[trio]" or "...[asyncio]"
        if "[trio]" in item.nodeid:
            deselected.append(item)
        else:
            kept.append(item)
    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = kept
