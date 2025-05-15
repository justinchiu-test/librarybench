import os
import tempfile
from backend_dev.microcli.i18n import load_translations

def test_no_dir(tmp_path):
    assert load_translations(str(tmp_path / "nonexistent")) == {}

def test_load_po(tmp_path):
    d = tmp_path / "locale"
    d.mkdir()
    f = d / "en.po"
    f.write_text("msgid \"hi\"\nmsgstr \"hello\"")
    trans = load_translations(str(d))
    assert "en.po" in trans
    assert "msgstr" in trans["en.po"]
