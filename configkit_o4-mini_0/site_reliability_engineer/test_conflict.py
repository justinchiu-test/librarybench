import pytest
from srectl.conflict import ConflictReporting

def test_no_conflict():
    config = {
        'alert': {'threshold': 0.2},
        'circuit_breaker': {'error_rate': 0.1},
        'alerts': [
            {'name': 'a', 'depends_on': []},
            {'name': 'b', 'depends_on': ['a']}
        ]
    }
    # threshold > error_rate OK, no cycle
    ConflictReporting.detect(config)

def test_contradictory_sla():
    config = {
        'alert': {'threshold': 0.05},
        'circuit_breaker': {'error_rate': 0.1},
    }
    with pytest.raises(ValueError):
        ConflictReporting.detect(config)

def test_circular_dependency():
    config = {
        'alert': {'threshold': 0.2},
        'circuit_breaker': {'error_rate': 0.1},
        'alerts': [
            {'name': 'a', 'depends_on': ['b']},
            {'name': 'b', 'depends_on': ['a']}
        ]
    }
    with pytest.raises(ValueError):
        ConflictReporting.detect(config)
