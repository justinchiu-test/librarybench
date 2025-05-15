import json
import os
import configparser
from datapipeline_cli.config_parser import parse_config_files

def test_parse_json(tmp_path):
    f = tmp_path / 'cfg.json'
    data = {'a': 1, 'b': 'x'}
    f.write_text(json.dumps(data))
    res = parse_config_files([str(f)])
    assert res == data

def test_parse_ini(tmp_path):
    f = tmp_path / 'cfg.ini'
    cfg = configparser.ConfigParser()
    cfg['default'] = {'a': '1', 'b': 'x'}
    with open(f, 'w') as fp:
        cfg.write(fp)
    res = parse_config_files([str(f)])
    assert res == {'a': '1', 'b': 'x'}

def test_parse_multiple(tmp_path):
    # JSON then INI, ini overrides
    j = tmp_path / 'a.json'
    j.write_text(json.dumps({'a': 1, 'b': 2}))
    ini = tmp_path / 'b.ini'
    cfg = configparser.ConfigParser()
    cfg['default'] = {'b': 'x', 'c': 'y'}
    with open(ini, 'w') as fp:
        cfg.write(fp)
    res = parse_config_files([str(j), str(ini)])
    assert res == {'a': 1, 'b': 'x', 'c': 'y'}
