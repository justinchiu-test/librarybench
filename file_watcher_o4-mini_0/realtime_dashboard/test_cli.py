import pytest
import asyncio
from filewatcher.cli import CLIInterface, main

@pytest.mark.asyncio
async def test_parse_and_run(tmp_path, monkeypatch):
    d = tmp_path / "d"
    d.mkdir()
    f = d / "x.txt"
    f.write_text("v")
    # monkeypatch print to capture output
    printed = []
    monkeypatch.setattr("builtins.print", lambda x: printed.append(x))
    result = await CLIInterface([str(d), "--include", "*.txt"]).run()
    assert isinstance(result, list)
    assert result
    # test main entry
    res2 = main([str(d)])
    assert isinstance(res2, list)
