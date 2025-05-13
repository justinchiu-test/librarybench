import os
from adapters.devops_engineer.devops_cli.env import env_override

def test_env_override():
    import os
    config = {"sec": {"key": "val", "other": "o"}}
    os.environ["DEVOPS_KEY"] = "OV"
    from adapters.devops_engineer.devops_cli.env import env_override
    new = env_override(config)
    assert new["sec"]["key"] == "OV"
    assert new["sec"]["other"] == "o"