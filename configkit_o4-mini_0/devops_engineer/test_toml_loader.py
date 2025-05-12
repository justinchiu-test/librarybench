import pytest
from config_framework.toml_loader import TOMLLoader

def test_load(tmp_path):
    content = '''
[section]
key = "value"
num = 10
'''
    file_path = tmp_path / "test.toml"
    file_path.write_text(content)
    loader = TOMLLoader(str(file_path))
    config = loader.load()
    assert 'section' in config
    assert config['section']['key'] == "value"
    assert config['section']['num'] == 10
