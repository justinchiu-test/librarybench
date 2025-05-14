import tempfile
from compliance_repo.store import ComplianceStore

def test_backup_restore_integrity():
    cs = ComplianceStore()
    cs.updateDocument('a', {'v':10})
    tmp = tempfile.NamedTemporaryFile(delete=False)
    tmp.close()
    cs.backup(tmp.name)
    cs.updateDocument('a', {'v':20})
    cs.restore(tmp.name)
    assert cs.getDocument('a')['v']==10
