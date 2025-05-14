import pytest
from src.personas.ops_engineer.cli_toolkit.config_parser import InfraConfigParser
from src.core.config.parser import ConfigParser

json_str = '{"a":1,"b":2}'
ini_str = "[section]\na=10\nb=20\n"
yaml_str = "x: 5\ny: true\n"
toml_str = "foo = \"bar\"\nnum = 3\n"

def test_parse_json(tmp_path):
    # Create a JSON file
    json_file = tmp_path / "config.json"
    json_file.write_text(json_str)
    
    # Use the InfraConfigParser to load it
    parser = InfraConfigParser(config_dir=str(tmp_path))
    config = parser.load_config("config")
    
    assert config["a"] == 1
    assert config["b"] == 2

def test_parse_ini(tmp_path):
    # Create an INI file
    ini_file = tmp_path / "config.ini"
    ini_file.write_text(ini_str)
    
    # Use the InfraConfigParser to load it
    parser = InfraConfigParser(config_dir=str(tmp_path))
    config = parser.load_config("config")
    
    assert "section" in config
    assert config["section"]["a"] == "10"

def test_parse_yaml(tmp_path):
    try:
        import yaml  # noqa
    except ImportError:
        pytest.skip("PyYAML not installed")
    
    # Create a YAML file
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_str)
    
    # Use the InfraConfigParser to load it
    parser = InfraConfigParser(config_dir=str(tmp_path))
    config = parser.load_config("config")
    
    assert config["x"] == 5
    assert config["y"] == True

def test_parse_toml(tmp_path):
    try:
        import toml  # noqa
    except ImportError:
        pytest.skip("toml not installed")
    
    # Create a TOML file
    toml_file = tmp_path / "config.toml"
    toml_file.write_text(toml_str)
    
    # Use the InfraConfigParser to load it
    parser = InfraConfigParser(config_dir=str(tmp_path))
    config = parser.load_config("config")
    
    assert config["foo"] == "bar"
    assert config["num"] == 3

def test_merge_dicts():
    a = {'x':1, 'nested': {'a':1}}
    b = {'y':2, 'nested': {'b':2}}
    merged = ConfigParser.merge_configs(a, b)
    assert merged['x'] == 1
    assert merged['y'] == 2
    assert merged['nested']['a'] == 1 and merged['nested']['b'] == 2