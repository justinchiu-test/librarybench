import os
import json
import tempfile
import pytest
from Software_Developer.env_manager import EnvironmentManager

@pytest.fixture
def tmp_env_dir(tmp_path):
    d = tmp_path / "envs"
    return str(d)

def make_config(tmp_path, name, deps=None):
    data = {"name": name}
    if deps is not None:
        data["dependencies"] = deps
    f = tmp_path / f"{name}.json"
    with open(f, "w") as fp:
        json.dump(data, fp)
    return str(f), data

def test_import_list_delete(tmp_path, tmp_env_dir):
    # setup
    em = EnvironmentManager(base_dir=tmp_env_dir)
    # import
    cfg_path, data = make_config(tmp_path, "testenv", {"a": ">=1.0"})
    name = em.import_env(cfg_path)
    assert name == "testenv"
    # list
    lst = em.list_envs()
    assert lst == ["testenv"]
    # get_env
    got = em.get_env("testenv")
    assert got == data
    # delete
    em.delete_env("testenv")
    assert em.list_envs() == []
    # delete non-existent
    with pytest.raises(FileNotFoundError):
        em.delete_env("noenv")
    # import missing file
    with pytest.raises(FileNotFoundError):
        em.import_env("nofile.json")
    # import without name
    bad = tmp_path / "bad.json"
    with open(bad, "w") as f:
        json.dump({}, f)
    with pytest.raises(ValueError):
        em.import_env(str(bad))
