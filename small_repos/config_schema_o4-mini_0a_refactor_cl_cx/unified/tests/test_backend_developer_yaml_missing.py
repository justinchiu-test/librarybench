import pytest
from configschema.loader import load_config
def test_no_yaml_support(tmp_path, monkeypatch):
    # simulate missing yaml support
    # remove YAML support in loader
    monkeypatch.setattr('configschema.loader.yaml', None)
    p = tmp_path / "c.yml"
    p.write_text("a: 1")
    with pytest.raises(RuntimeError):
        load_config(str(p))
