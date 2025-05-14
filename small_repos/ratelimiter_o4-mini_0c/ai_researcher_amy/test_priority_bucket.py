from ratelimiter.priority_bucket import PriorityBucket

def test_priority_bucket_low():
    pb = PriorityBucket(1, 1, priority_override=False)
    assert pb.allow(priority=False)
    pb._tokens = 0
    assert not pb.allow(priority=False)

def test_priority_bucket_high():
    pb = PriorityBucket(1, 1, priority_override=True)
    pb._tokens = 0
    assert pb.allow(priority=True)
