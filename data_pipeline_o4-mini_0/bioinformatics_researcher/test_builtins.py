import pytest
from pipeline.builtins import batch_reads, sort_reads, group_reads

def test_batch_reads():
    reads = list(range(10))
    batches = batch_reads(reads, batch_size=3)
    assert len(batches) == 4
    assert batches[0] == [0, 1, 2]
    assert batches[-1] == [9]

def test_sort_reads():
    reads = [
        {'chr': '2', 'pos': 200}, {'chr': '1', 'pos': 100}, {'chr': '1', 'pos': 50}
    ]
    sorted_reads = sort_reads(reads)
    assert sorted_reads[0]['pos'] == 50
    assert sorted_reads[1]['pos'] == 100
    assert sorted_reads[2]['pos'] == 200

def test_group_reads():
    reads = [
        {'gene': 'g1', 'seq': 'A'}, {'gene': 'g2', 'seq': 'C'}, {'gene': 'g1', 'seq': 'G'}
    ]
    groups = group_reads(reads)
    assert set(groups.keys()) == {'g1', 'g2'}
    assert len(groups['g1']) == 2
