from pipeline.sorting import BuiltInSort

def test_sort_ascending_descending():
    recs = [{"x": 3}, {"x": 1}, {"x": 2}]
    sorter = BuiltInSort(key="x")
    assert [r["x"] for r in sorter.sort(recs)] == [1,2,3]
    sorter_desc = BuiltInSort(key="x", reverse=True)
    assert [r["x"] for r in sorter_desc.sort(recs)] == [3,2,1]
