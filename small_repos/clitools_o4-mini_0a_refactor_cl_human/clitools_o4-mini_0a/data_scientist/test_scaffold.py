import os
import pytest
from datapipeline_cli.scaffold import gen_scaffold

def test_gen_scaffold(tmp_path):
    base = gen_scaffold(str(tmp_path), 'proj')
    pyproject = os.path.join(base, 'pyproject.toml')
    cfg = os.path.join(base, 'test_config.yaml')
    assert os.path.isdir(base)
    assert os.path.isfile(pyproject)
    assert os.path.isfile(cfg)
    content = open(pyproject).read()
    assert 'name = "proj"' in content
