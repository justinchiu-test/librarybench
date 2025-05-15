import os
import json
import tempfile
import pytest

from localcli import __version__
from localcli.features import (
    bump_version, gen_scaffold, publish_package, gen_config_schema,
    validate_config, format_help, load_translations, handle_signals,
    init_di, parse_config_files, manage_secrets, register_subcommands,
    env_override
)

def test_version():
    assert isinstance(__version__, str)
    parts = __version__.split('.')
    assert len(parts) == 3

def test_bump_version():
    assert bump_version("0.0.0") == "0.0.1"
    assert bump_version("1.2.9") == "1.2.10"
    with pytest.raises(ValueError):
        bump_version("invalid")

def test_gen_scaffold():
    scaffold = gen_scaffold("proj")
    assert scaffold["name"] == "proj"
    files = scaffold["files"]
    assert "pyproject.toml" in files
    assert files["README.md"].startswith("# proj")

def test_publish_package():
    msg = publish_package("pkg", "1.0.0")
    assert "pkg" in msg and "1.0.0" in msg

def test_gen_and_validate_config_schema():
    fields = ["a", "b"]
    schema = gen_config_schema(fields)
    assert schema["type"] == "object"
    good = {"a": "x", "b": "y"}
    bad = {"a": 1}
    assert validate_config(good, schema) is True
    assert validate_config(bad, schema) is False

def test_format_help():
    text = "help me"
    assert format_help(text) == text
    md = format_help(text, fmt='md')
    assert "## Help" in md
    ansi = format_help(text, fmt='ansi')
    assert "\033[1m" in ansi
    with pytest.raises(ValueError):
        format_help(text, fmt='unknown')

def test_load_translations(tmp_path):
    po = tmp_path / "test.po"
    content = '\n'.join([
        'msgid "Hello"',
        'msgstr "Hola"',
        'msgid "Bye"',
        'msgstr "Adiós"'
    ])
    po.write_text(content, encoding='utf-8')
    trans = load_translations(str(po))
    assert trans["Hello"] == "Hola"
    assert trans["Bye"] == "Adiós"

def test_handle_signals():
    @handle_signals
    def f_ok():
        return "done"
    @handle_signals
    def f_fail():
        raise KeyboardInterrupt()
    assert f_ok() == "done"
    assert f_fail() == "Aborted"

def test_init_di():
    svc = {"a": 1}
    di = init_di(svc)
    assert di == svc and di is not svc

def test_parse_config_files_json(tmp_path):
    data = {"k": "v"}
    fp = tmp_path / "c.json"
    fp.write_text(json.dumps(data), encoding='utf-8')
    assert parse_config_files(str(fp)) == data

def test_parse_config_files_yaml(tmp_path):
    text = """
    # a comment
    key1: val1
    key2: val2
    """
    fp = tmp_path / "c.yaml"
    fp.write_text(text, encoding='utf-8')
    res = parse_config_files(str(fp))
    assert res["key1"] == "val1"
    assert res["key2"] == "val2"

def test_parse_config_files_toml(tmp_path):
    text = """
    # comment
    key1 = "val1"
    key2 = 'val2'
    """
    fp = tmp_path / "c.toml"
    fp.write_text(text, encoding='utf-8')
    res = parse_config_files(str(fp))
    assert res["key1"] == "val1"
    assert res["key2"] == "val2"

def test_manage_secrets_and_env_override(monkeypatch):
    svc = "testsvc"
    key = "secretkey"
    assert manage_secrets(svc, key) is True
    env_key = f"SECRET_{svc.upper()}"
    assert os.environ[env_key] == key
    # test override
    monkeypatch.setenv("MYVAR", "123")
    assert env_override("MYVAR", "x") == "123"
    assert env_override("NOEXIST", "def") == "def"

def test_register_subcommands():
    cmds = {"a": lambda: 1}
    out = register_subcommands(cmds)
    assert out == cmds and out is not cmds
