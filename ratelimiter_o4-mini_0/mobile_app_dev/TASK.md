# The Task

I am a Mobile App Developer building a high‐volume chat client. I want a lightweight rate limiter I can sprinkle around my network calls to prevent server overloading, observe remaining quota in the UI, and queue retries on flaky connections—all without crashing on multi‐threaded image downloads. This code repo delivers exactly that.

# The Requirements

* `get_remaining_quota()`        : Runtime Inspection – show real‐time tokens left for each API endpoint  
* `get_usage_stats()`            : Runtime Inspection – capture client‐side usage to debug over‐throttling  
* `next_available_timestamp()`   : Runtime Inspection – display retry countdown timer in the UI  
* `queue_request(request, priority, max_wait)`  
                                 : Request Queuing & Prioritization – retry queued requests with backoff and priority  
* `with RateLimiter(config) as rl:` 
                                 : Context Manager API – wrap network stack calls in `with` blocks  
* `ThreadSafeRateLimiter`        : Multi-Threaded Safety – safe to share limiter between main/UI and background threads  
* `LeakyBucketRateLimiter(drain_rate)`  
                                 : Leaky Bucket Strategy – smooth out accidental bursts from image preloaders  
* `enable_fault_tolerance(mode="local")`  
                                 : Fault-Tolerant Mode – fall back to on-device counters if remote store times out  
* `scope_by_key(user_id)`         : Per-Key Scoping – isolate chat rates per logged‐in user  
* `validate_limits(schema)`       : Validation & Schema Enforcement – sanity‐check mobile config on startup  
* `set_mock_clock(timestamp)`  
                                 : Testing Utilities – simulate slow networks and timeouts in UI tests  
* `FakeRateLimiter()`             : Testing Utilities – stub out network calls in unit tests  
* `TestRateLimiterFixture`        : Testing Utilities – end‐to‐end harness for simulator  
* `@default_limits(calls=60, period="1s")`  
                                 : Per-Function Default Limits – annotate all HTTP methods with sane defaults  
