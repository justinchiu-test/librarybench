import pytest
from src.interfaces.ux_prototyper.wizard_engine import WizardEngine

def test_invalid_transition_no_change():
    w = WizardEngine()
    w.current_state = 'X'
    w.define_transition('t1', 'A', 'B', 'go')
    result = w.trigger('go')
    assert result == 'X'