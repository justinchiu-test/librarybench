import pytest
from config.conflict import report_conflicts

def test_no_conflict():
    exps = [{'output_path': 'a'}, {'output_path': 'b'}]
    assert report_conflicts(exps) is False

def test_conflict():
    exps = [{'output_path': 'a'}, {'output_path': 'a'}]
    with pytest.raises(ValueError):
        report_conflicts(exps)
