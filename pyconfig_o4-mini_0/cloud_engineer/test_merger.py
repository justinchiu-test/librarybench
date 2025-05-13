from config_loader.merger import merge_configs

def test_merge_simple_override():
    a = {'x': 1, 'y': 2}
    b = {'y': 3, 'z': 4}
    assert merge_configs([a, b]) == {'x': 1, 'y': 3, 'z': 4}

def test_merge_nested_dict():
    a = {'db': {'host': 'a', 'port': 1}}
    b = {'db': {'port': 2}}
    assert merge_configs([a, b]) == {'db': {'host': 'a', 'port': 2}}

def test_list_replace():
    a = {'l': [1, 2]}
    b = {'l': [3]}
    assert merge_configs([a, b], list_strategy='replace')['l'] == [3]

def test_list_append():
    a = {'l': [1, 2]}
    b = {'l': [3]}
    assert merge_configs([a, b], list_strategy='append')['l'] == [1, 2, 3]

def test_list_unique():
    a = {'l': [1, 2]}
    b = {'l': [2, 3]}
    assert merge_configs([a, b], list_strategy='unique')['l'] == [1, 2, 3]
