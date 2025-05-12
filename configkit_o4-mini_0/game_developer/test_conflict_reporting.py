from config.conflict import ConflictReporter

def test_no_conflicts():
    transitions = {'A': 'B', 'B': 'C', 'C': 'D'}
    assert ConflictReporter.detect(transitions) == []

def test_simple_conflict():
    transitions = {'A': 'B', 'B': 'A'}
    conf = ConflictReporter.detect(transitions)
    assert ('A', 'B') in conf
