# The Task

I am an API Product Manager shaping our public developer portal. I want a turnkey rate‐limiting library we can embed in docs, demos, and server code—complete with reporting endpoints, schema validation, and fallback for demos if Redis is offline. This repo provides all building blocks to implement quotas, measure calls, and ship stable SDKs.

# The Requirements

* `get_token_count()`            : Runtime Inspection – power the `/metrics` endpoint  
* `get_usage_stats()`            : Runtime Inspection – feed dashboards on developer portal  
* `next_available_timestamp()`   : Runtime Inspection – surface retry‐after headers  
* `get_remaining_quota()`        : Runtime Inspection – show live “requests left” in docs  
* `queue_request(request, priority, max_wait)`  
                                 : Request Queuing & Prioritization – demo burst handling with queued back‐off  
* `with RateLimiter(config) as rl:` 
                                 : Context Manager API – enable self‐service SDK calls in examples  
* `ThreadSafeRateLimiter`        : Multi-Threaded Safety – safe for multi‐threaded sample applications  
* `LeakyBucketRateLimiter(drain_rate)`  
                                 : Leaky Bucket Strategy – protect back‐end in high‐traffic demos  
* `enable_fault_tolerance(mode="local")`  
                                 : Fault-Tolerant Mode – demo smoothly if Redis or database is down  
* `scope_by_key(developer_id)`    : Per-Key Scoping – isolate key‐based quotas per dev user  
* `validate_limits(schema)`       : Validation & Schema Enforcement – validate portal YAML configs  
* `set_mock_clock(timestamp)`  
                                 : Testing Utilities – simulate timeouts in live code examples  
* `FakeRateLimiter()`             : Testing Utilities – sandboxed limiter for quickstarts  
* `TestRateLimiterFixture`        : Testing Utilities – demo harness for CI/CD pipelines  
* `@default_limits(calls=1000, period="1h")`  
                                 : Per-Function Default Limits – embed default guards in sample endpoints  
