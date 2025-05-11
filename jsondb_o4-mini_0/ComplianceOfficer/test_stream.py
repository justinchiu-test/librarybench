from compliance_repo.store import ComplianceStore

def test_multiple_subscribers():
    cs = ComplianceStore()
    ev1 = []
    ev2 = []
    cs.streamChanges(ev1.append)
    cs.streamChanges(ev2.append)
    cs.updateDocument('s', {'k':9})
    assert ev1 and ev2
    assert ev1[0]['id']=='s'
    assert ev2[0]['type']=='update'
