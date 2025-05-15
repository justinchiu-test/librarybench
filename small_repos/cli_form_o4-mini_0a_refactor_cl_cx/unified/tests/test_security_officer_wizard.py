import pytest
from security_officer.incident_form.wizard import WizardLayout

def test_wizard_navigation():
    pages = ["A","B","C"]
    w = WizardLayout(pages)
    assert w.get_current_page() == "A"
    assert w.next_page() == "B"
    assert w.next_page() == "C"
    assert w.next_page() == "C"
    assert w.prev_page() == "B"
    assert w.prev_page() == "A"
    assert w.prev_page() == "A"

def test_wizard_invalid_init():
    with pytest.raises(ValueError):
        WizardLayout([])
