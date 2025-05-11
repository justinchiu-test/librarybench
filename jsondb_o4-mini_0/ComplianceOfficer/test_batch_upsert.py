from compliance_repo.store import ComplianceStore

def test_atomic_batch_upsert():
    cs = ComplianceStore()
    docs = [{'id':'a','x':1},{'id':'b','y':2}]
    cs.batchUpsert(docs)
    assert cs.getDocument('a')['x']==1
    assert cs.getDocument('b')['y']==2
    # versions counted
    assert len(cs.getVersions('a'))==1
    assert len(cs.getVersions('b'))==1
