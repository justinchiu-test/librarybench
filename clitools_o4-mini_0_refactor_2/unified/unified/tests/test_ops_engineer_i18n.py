import os
import tempfile
import pytest
from adapters.ops_engineer.cli_toolkit.i18n import load_translations

def test_load_translations(tmp_path):
    content = 'msgid "Hello"\nmsgstr "Hola"\n'
    file = tmp_path / "test.po"
    file.write_text(content, encoding='utf-8')
    d = load_translations(str(file))
    assert d["Hello"] == "Hola"

def test_load_missing_file():
    with pytest.raises(FileNotFoundError):
        load_translations("nonexistent.po")