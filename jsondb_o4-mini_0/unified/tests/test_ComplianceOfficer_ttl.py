import time
from ComplianceOfficer.compliance_repo.store import ComplianceStore

def test_multiple_ttl():
    cs = ComplianceStore()
    cs.updateDocument('a', {'v':1})
    cs.updateDocument('b', {'v':2})
    cs.setTTL('a', 0.1)
    cs.setTTL('b', 0.2)
    time.sleep(0.15)
    cs.purgeExpired()
    assert cs.getDocument('a') is None
    assert cs.getDocument('b') == {'v':2}
    time.sleep(0.1)
    cs.purgeExpired()
    assert cs.getDocument('b') is None
