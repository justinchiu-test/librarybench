from cli_framework.env import env_override

def test_env_override():
    env = {"SEC_FOO": "v1", "SEC_BAR": "v2", "OTHER": "x", "SEC_BAZ": "v3"}
    out = env_override(env, ["FOO", "BAZ"])
    assert out == {"FOO": "v1", "BAZ": "v3"}
