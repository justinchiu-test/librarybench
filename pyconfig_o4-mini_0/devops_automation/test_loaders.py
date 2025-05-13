import pytest
import os
from config_manager.loaders import register_loader, load_config

def test_loader_registration(tmp_path):
    file = tmp_path / "test.custom"
    file.write_text("data")
    def loader(path):
        return open(path).read() + "_ok"
    register_loader(".custom", loader)
    out = load_config(str(file))
    assert out == "data_ok"
    with pytest.raises(ValueError):
        load_config("noext.unknown")
