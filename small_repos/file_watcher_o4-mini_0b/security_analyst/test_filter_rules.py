import pytest
from config_watcher.filter_rules import FilterRules

def test_include_exclude_patterns():
    fr = FilterRules()
    fr.include('*.txt')
    fr.exclude('secret*.txt')
    assert fr.match('doc.txt')
    assert not fr.match('secret1.txt')
    fr2 = FilterRules()
    fr2.exclude('*.log')
    assert fr2.match('a.txt')
    assert not fr2.match('a.log')
