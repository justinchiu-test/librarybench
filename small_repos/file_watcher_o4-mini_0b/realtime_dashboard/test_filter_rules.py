from filewatcher.filter_rules import DynamicFilterRules

def test_include_exclude():
    fr = DynamicFilterRules()
    fr.add_include("*.txt")
    fr.add_exclude("secret*.txt")
    assert fr.match("test.txt")
    assert not fr.match("secret1.txt")
    # when no include patterns, all not excluded pass
    fr2 = DynamicFilterRules()
    fr2.add_exclude("*.log")
    assert fr2.match("foo.txt")
    assert not fr2.match("foo.log")
