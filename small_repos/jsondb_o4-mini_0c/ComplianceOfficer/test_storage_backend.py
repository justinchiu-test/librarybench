import os
import tempfile
from compliance_repo.store import ComplianceStore

def test_hsm_backend_behaves_like_memory():
    cs = ComplianceStore()
    cs.setStorageBackend('hsm')
    cs.updateDocument('h1', {'val':7})
    assert cs.getDocument('h1')['val']==7
