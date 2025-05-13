from streamkit.batch import BuiltInBatch
from streamkit.sort import BuiltInSort

def test_batch():
    b = BuiltInBatch(window_size=3)
    items = [1,2,3,4,5,6,7]
    assert b.batch(items) == [[1,2,3],[4,5,6],[7]]

def test_sort():
    s = BuiltInSort()
    items = [{'v':3},{'v':1},{'v':2}]
    sorted_items = s.sort(items, key=lambda x: x['v'])
    assert [i['v'] for i in sorted_items] == [1,2,3]
