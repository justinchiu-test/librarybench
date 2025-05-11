import os
from devops_cli.env import env_override

def test_env_override(tmp_env):
    config = {"sec": {"key": "val", "other": "o"}}
    os.environ["DEVOPS_KEY"] = "OV"
    new = env_override(config)
    assert new["sec"]["key"] == "OV"
    assert new["sec"]["other"] == "o"
