import os
import tempfile
from config.loaders import TOMLLoader

def test_toml_loader():
    content = """
    [level]
    name = "Test"
    number = 5
    """
    fd, path = tempfile.mkstemp(suffix=".toml")
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        data = TOMLLoader.load(path)
        assert 'level' in data
        assert data['level']['name'] == "Test"
        assert data['level']['number'] == 5
    finally:
        os.remove(path)
