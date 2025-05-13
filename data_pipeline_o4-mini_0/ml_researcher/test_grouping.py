from pipeline.grouping import BuiltInGroup

def test_group_single_key():
    recs = [{"k": 1}, {"k": 2}, {"k": 1}]
    grp = BuiltInGroup("k")
    result = grp.group(recs)
    assert set(result.keys()) == {1, 2}
    assert len(result[1]) == 2

def test_group_multiple_keys_and_aggregate():
    recs = [
        {"a": 1, "b": 2, "v": 10},
        {"a": 1, "b": 2, "v": 15},
        {"a": 2, "b": 3, "v": 5}
    ]
    grp = BuiltInGroup(["a", "b"])
    agg = grp.aggregate(recs, lambda rs: sum(r["v"] for r in rs))
    assert agg[(1,2)] == 25
    assert agg[(2,3)] == 5
