import os
import tempfile
from config_loader.loaders import load_toml, load_xml

def test_load_toml(tmp_path):
    content = "a = 1\nb = \"xyz\"\n"
    p = tmp_path / "t.toml"
    p.write_text(content)
    d = load_toml(str(p))
    assert d['a'] == 1
    assert d['b'] == "xyz"

def test_load_xml(tmp_path):
    content = "<root><a>1</a><b>xyz</b></root>"
    p = tmp_path / "x.xml"
    p.write_text(content)
    d = load_xml(str(p))
    assert 'root' in d
    assert d['root']['a'] == '1'
    assert d['root']['b'] == 'xyz'
