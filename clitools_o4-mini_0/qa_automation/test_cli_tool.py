import os
import signal
import tempfile
import json
import configparser
import pytest
from cli_tool import (
    register_subcommands, parse_config, configure_prompt,
    install_signal_handlers, register_plugin_hooks,
    collect_telemetry, record_telemetry, telemetry_data,
    register_aliases, aliases, CacheHelper,
    inject_common_flags, autobuild_parser, _before_hooks, _after_hooks
)
import argparse

def test_parse_config_json(tmp_path):
    data = {'a': 1, 'b': 'two'}
    p = tmp_path / "conf.json"
    p.write_text(json.dumps(data))
    res = parse_config(str(p))
    assert res == data

def test_parse_config_ini(tmp_path):
    content = "[sec]\nx=1\ny=hello"
    p = tmp_path / "conf.ini"
    p.write_text(content)
    res = parse_config(str(p))
    assert 'sec' in res
    assert res['sec']['x'] == '1'
    assert res['sec']['y'] == 'hello'

def test_parse_config_yaml(tmp_path):
    content = "a: 10\nb: foo"
    p = tmp_path / "conf.yaml"
    p.write_text(content)
    res = parse_config(str(p))
    assert res['a'] == 10
    assert res['b'] == 'foo'

def test_parse_config_toml(tmp_path):
    content = "a = 5\nb = 'bar'"
    p = tmp_path / "conf.toml"
    p.write_text(content)
    res = parse_config(str(p))
    assert res['a'] == 5
    assert res['b'] == 'bar'

def test_configure_prompt_yes(monkeypatch, capsys):
    monkeypatch.setattr('builtins.input', lambda x: 'Y')
    ok = configure_prompt("Summary")
    captured = capsys.readouterr()
    assert "Summary" in captured.out
    assert ok

def test_configure_prompt_no(monkeypatch, capsys):
    monkeypatch.setattr('builtins.input', lambda x: 'n')
    ok = configure_prompt("Summary")
    assert not ok

def test_install_signal_handlers(tmp_path, capsys):
    called = {'cleaned': False}
    def cleanup():
        called['cleaned'] = True
    old = install_signal_handlers(cleanup)
    # simulate signal
    handler = signal.getsignal(signal.SIGINT)
    handler(signal.SIGINT, None)
    out = capsys.readouterr().out
    assert "Testing aborted" in out
    assert called['cleaned']
    # restore old handlers
    for sig, h in old.items():
        signal.signal(sig, h)

def test_register_plugin_hooks():
    _before_hooks.clear()
    _after_hooks.clear()
    def b(): pass
    def a(): pass
    register_plugin_hooks(before=b, after=a)
    assert b in _before_hooks
    assert a in _after_hooks

def test_collect_telemetry():
    telemetry_data.clear()
    collect_telemetry(True)
    record_telemetry({'event': 't1'})
    assert telemetry_data and telemetry_data[-1]['event'] == 't1'
    collect_telemetry(False)
    record_telemetry({'event': 't2'})
    assert telemetry_data[-1]['event'] != 't2'

def test_register_aliases():
    aliases.clear()
    register_aliases({'tr':'test run', 'ts':'test smoke'})
    assert aliases['tr'] == 'test run'
    assert aliases['ts'] == 'test smoke'

def test_cache_helper_memory(tmp_path):
    c = CacheHelper(use_disk=False)
    c.set('k1', 123)
    assert c.get('k1') == 123
    assert c.get('unknown') is None

def test_cache_helper_disk(tmp_path, monkeypatch):
    # redirect cache_dir to tmp_path
    import cli_tool
    monkeypatch.setattr(cli_tool, 'cache_dir', str(tmp_path))
    c = CacheHelper(use_disk=True)
    c.set('k2', {'x':1})
    # clear in-memory to force load from disk
    c.store.clear()
    val = c.get('k2')
    assert val == {'x':1}

def test_inject_common_flags():
    p = argparse.ArgumentParser()
    inject_common_flags(p)
    opts = [a.dest for a in p._actions]
    assert 'version' in opts
    assert 'verbose' in opts
    assert 'quiet' in opts

def test_autobuild_parser():
    spec = [
        {'name': 'foo', 'type': int, 'help': 'foo val'},
        {'name': '--bar', 'choices': ['x','y'], 'default': 'x', 'help': 'bar opt'}
    ]
    p = autobuild_parser(spec)
    args = p.parse_args(['5', '--bar', 'y'])
    assert args.foo == 5
    assert args.bar == 'y'

def test_register_subcommands():
    main = argparse.ArgumentParser()
    sub = main.add_subparsers(dest='cmd')
    register_subcommands(sub)
    args = main.parse_args(['test', 'run', '--env', 'prod', '--rerun'])
    assert args.cmd == 'test'
    assert args.test_cmd == 'run'
    assert args.env == 'prod'
    assert args.rerun
