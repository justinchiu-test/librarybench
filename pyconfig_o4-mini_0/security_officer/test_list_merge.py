from config_framework.list_merge import merge_list

def test_unique_merge():
    d = [1,2]
    o = [2,3]
    merged = merge_list(d, o, unique=True)
    assert set(merged) == {1,2,3}

def test_replace_merge():
    d = [1,2]
    o = [2,3]
    merged = merge_list(d, o, unique=False)
    assert merged == o

def test_no_override():
    d = [1,2]
    merged = merge_list(d, None)
    assert merged == d
