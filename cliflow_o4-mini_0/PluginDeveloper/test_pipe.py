import sys
import io
import json
import pytest
from plugin_framework.decorators import pipe

def test_pipe_with_arg():
    @pipe
    def echo(data):
        return data
    assert echo([1, 2, 3]) == [1,2,3]

def test_pipe_from_stdin(monkeypatch):
    data = {'x': 10}
    buf = io.StringIO(json.dumps(data))
    monkeypatch.setattr(sys, 'stdin', buf)
    @pipe
    def reader(d):
        return d
    out = reader()
    assert out == data
