import pytest
from watcher.filters import FilterRules

def test_default_filter():
    fr = FilterRules()
    assert fr.match("file.txt")
    assert not fr.match(".secret")
    assert not fr.match("dir/.git")

def test_include_exclude():
    fr = FilterRules(include=["*.txt"], exclude=["a*.txt"], hide_dotfiles=False)
    assert fr.match("file.txt")
    assert not fr.match("a.txt")
    assert not fr.match("b.py")

def test_dynamic_rules():
    fr = FilterRules()
    fr.add_exclude("*.log")
    assert not fr.match("error.log")
    fr.remove_exclude("*.log")
    assert fr.match("error.log")
