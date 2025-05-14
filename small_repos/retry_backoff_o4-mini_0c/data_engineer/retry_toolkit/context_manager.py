import time
import linecache

class retry_context:
    """
    Retry any exception (except StopIteration) up to max_attempts times.
    On success (no exception) we exit; on exhausting retries or a stop_condition,
    we re‐raise the last exception.
    """

    def __init__(self, max_attempts=3, backoff=None, stop_condition=None):
        self.max_attempts = max_attempts
        # backoff is a callable that takes attempt number
        self.backoff = backoff or (lambda x: 0)
        # optional stop condition: callable(attempts, last_exception) -> bool
        self.stop_condition = stop_condition
        self.attempts = 0

    def __enter__(self):
        # Nothing special to return; user just writes work() in the block
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        # If no exception, nothing to do
        if exc_type is None:
            return False
        # Don't swallow StopIteration
        if issubclass(exc_type, StopIteration):
            return False

        # Count this failure
        self.attempts += 1

        # Honor a user‐provided stop condition
        if self.stop_condition and self.stop_condition(self.attempts, exc_val):
            # propagate
            return False

        # If we've reached the max, propagate
        if self.attempts >= self.max_attempts:
            return False

        # Otherwise, wait and retry
        time.sleep(self.backoff(self.attempts))

        # Attempt to re‐invoke the same function call that failed.
        # We look at the source line, grab the function name, and call it.
        frame = exc_tb.tb_frame
        lineno = exc_tb.tb_lineno
        filename = frame.f_code.co_filename
        line = linecache.getline(filename, lineno).strip()
        func_name = None
        if '(' in line:
            func_name = line.split('(')[0].strip()

        fn = None
        if func_name:
            fn = frame.f_locals.get(func_name) or frame.f_globals.get(func_name)

        if fn and callable(fn):
            try:
                fn()
            except Exception as e2:
                # If it fails again, recurse to handle next retry or final fail
                return self.__exit__(type(e2), e2, e2.__traceback__)
            else:
                # succeeded on retry, suppress the original exception
                return True

        # Could not retry (e.g., unparsable line), propagate
        return False
