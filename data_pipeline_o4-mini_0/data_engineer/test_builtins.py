from pipeline.builtins import BatchStage, SortStage, GroupStage

def test_batch():
    stage = BatchStage(3)
    out = stage.process([1,2,3,4,5,6,7])
    assert out == [[1,2,3],[4,5,6],[7]]

def test_sort():
    data = [{'v':3},{'v':1},{'v':2}]
    out = SortStage('v').process(data)
    assert [d['v'] for d in out] == [1,2,3]

def test_group():
    data = [{'k':1,'v':10},{'k':2,'v':20},{'k':1,'v':30}]
    groups = GroupStage('k').process(data)
    # two groups
    lengths = sorted([len(g) for g in groups])
    assert lengths == [1,2]
