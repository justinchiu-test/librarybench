from config_manager.merge import merge_configs

def test_merge_ignores_non_dicts():
    assert merge_configs({"a":1}, None, "str") == {"a":1}
