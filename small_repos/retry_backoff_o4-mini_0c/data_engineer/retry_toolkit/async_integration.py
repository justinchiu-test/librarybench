import asyncio
import linecache

class async_retry_context:
    """
    Async version of retry_context: catches plain Exceptions (not StopIteration),
    retries up to max_attempts, re‐raises on stop_condition or exhaustion.
    """
    def __init__(self, max_attempts=3, backoff=None, stop_condition=None):
        self.max_attempts = max_attempts
        # backoff is a callable that takes attempt number
        self.backoff = backoff or (lambda x: 0)
        # optional stop condition: callable(attempts, last_exception) -> bool
        self.stop_condition = stop_condition
        self.attempts = 0

    async def __aenter__(self):
        # nothing to do on enter
        return None

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # No exception: propagate normal exit
        if exc_type is None:
            return False

        # Don't swallow StopIteration
        if issubclass(exc_type, StopIteration):
            return False

        # Count this failure
        self.attempts += 1

        # Honor user‐provided stop condition
        if self.stop_condition and self.stop_condition(self.attempts, exc_val):
            return False  # propagate

        # If we've reached max, propagate
        if self.attempts >= self.max_attempts:
            return False

        # Otherwise back off and retry
        await asyncio.sleep(self.backoff(self.attempts))

        # Try to re‐invoke the same coroutine call that failed by
        # inspecting the traceback source line
        frame = exc_tb.tb_frame
        lineno = exc_tb.tb_lineno
        filename = frame.f_code.co_filename
        raw = linecache.getline(filename, lineno).strip()

        # strip off any "await " and any assignment before it
        line = raw
        if 'await ' in line:
            # find the last 'await ' (so we ignore left‐hand side)
            idx = line.rfind('await ')
            line = line[idx + len('await '):].lstrip()

        # now extract function name
        func_name = None
        if '(' in line:
            func_name = line.split('(', 1)[0].strip()

        fn = None
        if func_name:
            fn = frame.f_locals.get(func_name) or frame.f_globals.get(func_name)

        if fn and callable(fn):
            # If it's an async function, await it; otherwise, call sync
            try:
                if asyncio.iscoroutinefunction(fn):
                    await fn()
                else:
                    fn()
            except Exception as e2:
                # on second failure, recurse to decide further retries or final propagate
                return await self.__aexit__(type(e2), e2, e2.__traceback__)
            else:
                # succeeded on retry: suppress original exception
                return True

        # Could not retry (unparsable line, etc.), propagate
        return False
