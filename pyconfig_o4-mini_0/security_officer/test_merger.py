from config_framework.merger import merge_configs

def test_merge_precedence():
    defaults = {"a": 1, "b": 2}
    vault = {"b": 20, "c": 30}
    env = {"c": 300}
    merged = merge_configs(defaults, vault, env)
    assert merged == {"a": 1, "b": 20, "c": 300}
