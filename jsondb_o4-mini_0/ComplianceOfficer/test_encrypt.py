import json
from compliance_repo.store import ComplianceStore

def test_encrypt_decrypt_cycle():
    cs = ComplianceStore()
    key = b'secret'
    cs.encryptAtRest(key)
    cs.updateDocument('e1', {'d':'data'})
    # simulate reading raw
    enc = cs._store['e1']
    assert isinstance(enc, bytes)
    dec = cs._decrypt(enc)
    payload = json.loads(dec.decode())
    assert payload == {'d':'data'}
