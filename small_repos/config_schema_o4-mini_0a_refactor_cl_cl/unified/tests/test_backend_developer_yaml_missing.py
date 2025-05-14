import pytest
from backend_developer.configmanager import load_config
def test_no_yaml_support(tmp_path, monkeypatch):
    # simulate missing yaml
    monkeypatch.setattr('configmanager.config.yaml', None)
    p = tmp_path / "c.yml"
    p.write_text("a: 1")
    with pytest.raises(RuntimeError):
        load_config(str(p))
