from compliance_repo.store import ComplianceStore

def test_register_and_trigger():
    cs = ComplianceStore()
    triggered = []
    def p(evt): triggered.append(evt['id'])
    cs.registerPlugin(p)
    cs.updateDocument('pid', {'x':5})
    assert 'pid' in triggered
