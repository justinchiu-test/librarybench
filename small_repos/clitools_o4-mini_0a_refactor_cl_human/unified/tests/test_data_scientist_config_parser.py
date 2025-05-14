import json
import os
import configparser
from src.personas.data_scientist.datapipeline_cli.config_parser import DataPipelineConfigParser

def test_parse_json(tmp_path):
    f = tmp_path / 'cfg.json'
    data = {'a': 1, 'b': 'x'}
    f.write_text(json.dumps(data))
    parser = DataPipelineConfigParser(config_dir=str(tmp_path))
    res = parser.load_config("cfg")
    assert res == data

def test_parse_ini(tmp_path):
    f = tmp_path / 'cfg.ini'
    cfg = configparser.ConfigParser()
    cfg['default'] = {'a': '1', 'b': 'x'}
    with open(f, 'w') as fp:
        cfg.write(fp)
    parser = DataPipelineConfigParser(config_dir=str(tmp_path))
    res = parser.load_config("cfg")
    assert res == {'a': '1', 'b': 'x'}

def test_parse_multiple(tmp_path):
    # Create base config
    j = tmp_path / 'pipeline.json'
    j.write_text(json.dumps({'a': 1, 'b': 2}))
    
    # Create environment-specific config
    ini = tmp_path / 'pipeline-development.ini'
    cfg = configparser.ConfigParser()
    cfg['default'] = {'b': 'x', 'c': 'y'}
    with open(ini, 'w') as fp:
        cfg.write(fp)
    
    # Load with merged configs
    parser = DataPipelineConfigParser(config_dir=str(tmp_path))
    res = parser.load_config("pipeline")
    
    # Verify merged result
    assert res['a'] == 1
    assert res['b'] == 'x'  # Overridden by the ini file
    assert res['c'] == 'y'  # Added by the ini file