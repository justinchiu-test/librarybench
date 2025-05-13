import sys
import contextlib

class redirect_io:
    def __init__(self, stdin=None, stdout=None, stderr=None):
        self._new_stdin = stdin
        self._new_stdout = stdout
        self._new_stderr = stderr
        self._old_stdin = None
        self._stdout_cm = None
        self._stderr_cm = None

    def __enter__(self):
        if self._new_stdin is not None:
            self._old_stdin = sys.stdin
            sys.stdin = self._new_stdin
        if self._new_stdout is not None:
            self._stdout_cm = contextlib.redirect_stdout(self._new_stdout)
            self._stdout_cm.__enter__()
        if self._new_stderr is not None:
            self._stderr_cm = contextlib.redirect_stderr(self._new_stderr)
            self._stderr_cm.__enter__()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._stderr_cm is not None:
            self._stderr_cm.__exit__(exc_type, exc, tb)
        if self._stdout_cm is not None:
            self._stdout_cm.__exit__(exc_type, exc, tb)
        if self._new_stdin is not None:
            import sys as _sys
            _sys.stdin = self._old_stdin
