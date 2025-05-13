# The Task

I am a Data Scientist running distributed web scrapers and model inference pipelines. I want to throttle my API queries, keep a per‐model token ledger, and test edge‐cases to avoid blacklisting. This code repository gives me dynamic inspection, key scoping, fault tolerance, plus fixtures to simulate bursts and downtime.

# The Requirements

* `get_token_count()`            : Runtime Inspection – monitor how many queries remain per API  
* `get_usage_stats()`            : Runtime Inspection – log consumption for each model  
* `next_available_timestamp()`   : Runtime Inspection – check when I can next call `predict()`  
* `get_remaining_quota()`        : Runtime Inspection – track budget per pipeline run  
* `queue_request(query, priority, max_wait)`  
                                 : Request Queuing & Prioritization – enqueue extra queries with priority handling  
* `with RateLimiter(config) as rl:` 
                                 : Context Manager API – wrap scraping and inference calls  
* `ThreadSafeRateLimiter`        : Multi-Threaded Safety – share limiter across parallel Dask workers  
* `LeakyBucketRateLimiter(drain_rate)`  
                                 : Leaky Bucket Strategy – keep a steady stream of calls to APIs  
* `enable_fault_tolerance(mode="local")`  
                                 : Fault-Tolerant Mode – degrade to in‐memory counters if Redis dies  
* `scope_by_key(api_key)`         : Per-Key Scoping – separate quotas per external service key  
* `validate_limits(schema)`       : Validation & Schema Enforcement – catch bad limit definitions early  
* `set_mock_clock(timestamp)`  
                                 : Testing Utilities – fast-forward time in unit tests  
* `FakeRateLimiter()`             : Testing Utilities – fake limiting behavior in notebook tests  
* `TestRateLimiterFixture`        : Testing Utilities – integration test fixture for distributed runs  
* `@default_limits(calls=200, period="10m")`  
                                 : Per-Function Default Limits – annotate heavy scrapers with defaults  
