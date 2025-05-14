import pytest
from watcher import DynamicFilterRules

def test_default_patterns():
    f = DynamicFilterRules()
    assert f.match("doc.md")
    assert f.match("notebook.ipynb")
    assert not f.match("image.png")

def test_include_exclude_dynamic():
    f = DynamicFilterRules(include_patterns=["*.txt"], exclude_patterns=["a.txt"])
    assert f.match("b.txt")
    assert not f.match("a.txt")
    f.include("a.txt")
    assert f.match("a.txt")
    f.exclude("b.txt")
    assert not f.match("b.txt")
