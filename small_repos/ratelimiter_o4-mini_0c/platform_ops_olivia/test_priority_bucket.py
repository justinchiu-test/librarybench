from ratelimiter.buckets import PriorityBucket

def test_priority_bucket_allows_unlimited():
    bucket = PriorityBucket()
    for _ in range(1000):
        assert bucket.allow()
