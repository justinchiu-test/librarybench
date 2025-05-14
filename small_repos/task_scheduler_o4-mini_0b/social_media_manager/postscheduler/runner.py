import asyncio

def run_coroutine(coros):
    """
    coros: list of coroutine objects
    returns list of results if called in a sync context,
    or an awaitable when called within an existing event loop.
    """
    try:
        # If we're in a running loop, return an awaitable
        asyncio.get_running_loop()
    except RuntimeError:
        # No event loop running: create one, run tasks, and return results
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(asyncio.gather(*coros))
        finally:
            loop.close()
    else:
        # Event loop is running: return a gather awaitable
        return asyncio.gather(*coros)
