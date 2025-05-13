from streamkit.filtering import BuiltInFilter
from streamkit.mapping import BuiltInMap

def test_filter_and_map():
    items = [1,2,3,4]
    f = BuiltInFilter(predicate=lambda x: x % 2 == 0)
    m = BuiltInMap(map_fn=lambda x: x * 10)
    filtered = f.filter(items)
    assert filtered == [2,4]
    mapped = m.map(filtered)
    assert mapped == [20,40]
