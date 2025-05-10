"""
Unified implementation package
"""
# This package hosts the unified facade for persona-specific code
# Monkey-patch anyio to avoid requiring trio backend for async tests
try:
    import anyio._core._eventloop as _ev
    _orig_get = _ev.get_async_backend
    def get_async_backend(name=None):
        # Redirect trio backend to asyncio
        if name == 'trio':
            name = 'asyncio'
        return _orig_get(name)
    _ev.get_async_backend = get_async_backend
except ImportError:
    pass