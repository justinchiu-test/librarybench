import os
import sys
from datapipeline_cli.commands import main

def test_main_extract(tmp_path, capsys):
    res = main(['extract', '--param', 'foo'])
    out = capsys.readouterr().out
    assert "{'action': 'extract', 'param': 'foo'}" in out
    assert res == {'action': 'extract', 'param': 'foo'}

def test_main_default_param(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv('PARAM', 'envval')
    res = main(['extract'])
    out = capsys.readouterr().out
    assert 'envval' in out
    assert res['param'] == 'envval'

def test_main_version(tmp_path, capsys, monkeypatch):
    # create version.txt
    monkeypatch.chdir(tmp_path)
    with open('version.txt', 'w') as f:
        f.write('9.9.9')
    main(['--version'])
    out = capsys.readouterr().out.strip()
    assert out == '9.9.9'
