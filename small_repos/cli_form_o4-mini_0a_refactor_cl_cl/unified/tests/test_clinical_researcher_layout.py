from clinical_researcher.form_system.layout import WizardLayout

def test_wizard_navigation():
    pages = [['a'], ['b', 'c'], ['d']]
    wiz = WizardLayout(pages)
    assert wiz.get_current_page() == ['a']
    assert wiz.next_page() == ['b', 'c']
    assert wiz.next_page() == ['d']
    # further next_page stays on last
    assert wiz.next_page() == ['d']
    assert wiz.prev_page() == ['b', 'c']
    assert wiz.prev_page() == ['a']
    # prev_page at first stays
    assert wiz.prev_page() == ['a']
