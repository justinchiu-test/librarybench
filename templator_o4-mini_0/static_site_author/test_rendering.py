import os
import tempfile
import threading
import asyncio
import importlib.util
import pytest
from static_site_engine import render_to_string, render_threadsafe, render_async, render_to_file

def test_render_to_string():
    tpl = "Hello, {name}!"
    out = render_to_string(tpl, name="Tester")
    assert out == "Hello, Tester!"

def test_render_threadsafe():
    tpl = "Count: {n}"
    results = []
    def worker(n):
        results.append(render_threadsafe(tpl, n=n))
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sorted(results) == [f"Count: {i}" for i in range(5)]

@pytest.mark.asyncio
async def test_render_async():
    tpl = "Async {val}"
    coro = render_async(tpl, val=42)
    result = await coro
    assert result == "Async 42"

def test_render_to_file(tmp_path):
    tpl = "File {x}"
    file_path = tmp_path / "out" / "test.html"
    path = render_to_file(tpl, str(file_path), x=7)
    assert os.path.exists(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == "File 7"
