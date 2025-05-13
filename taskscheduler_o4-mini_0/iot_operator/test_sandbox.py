import tempfile
import os
import time
from iot_scheduler.sandbox import run_in_sandbox

def test_run_in_sandbox_success(tmp_path):
    script = tmp_path / "hello.py"
    script.write_text('print("hello")')
    code, out, err = run_in_sandbox(str(script))
    assert code == 0
    assert b"hello" in out

def test_run_in_sandbox_timeout(tmp_path):
    script = tmp_path / "sleep.py"
    script.write_text('import time; time.sleep(1)')
    code, out, err = run_in_sandbox(str(script), timeout=0.1)
    assert code == -1
