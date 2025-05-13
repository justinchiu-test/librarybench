import io
import sys
from plugin_framework.io_redirector import redirect_io

def test_redirect_stdout_stderr_stdin():
    inp = io.StringIO("inputdata")
    out = io.StringIO()
    err = io.StringIO()
    with redirect_io(stdin=inp, stdout=out, stderr=err):
        data = sys.stdin.read()
        print("hello")
        print("err", file=sys.stderr)
    assert data == "inputdata"
    assert out.getvalue().strip() == "hello"
    assert err.getvalue().strip() == "err"
