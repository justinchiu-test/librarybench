import asyncio
import os
import sys
import tempfile
import threading
import time
import pytest
from subprocess import Popen, PIPE

def test_cli_help():
    proc = Popen([sys.executable, "-c",
                  "import filewatcher.cli; print('ok')"], stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate(timeout=5)
    assert b"ok" in out
