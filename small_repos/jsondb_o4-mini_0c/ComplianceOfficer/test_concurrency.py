import threading
from compliance_repo.store import ComplianceStore

def test_locking_prevents_overlap():
    cs = ComplianceStore()
    cs.updateDocument('z', {'count':0})
    order = []
    def task():
        for _ in range(10):
            d = cs.getDocument('z')
            cs.updateDocument('z', {'count': d['count']+1})
            order.append(cs.getDocument('z')['count'])
    threads = [threading.Thread(target=task) for _ in range(3)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert cs.getDocument('z')['count']==30
    # ensure sequence 1..30 present
    assert sorted(order)==list(range(1,31))
