# The Task

I am an AI researcher training large language models in a distributed cluster. I want to be able to throttle inference calls per tenant while letting high-priority experiments burst when needed. This repository offers a unified interface for sync and async code, with full test harness and observability.

# The Requirements

* `MockableClock` : Advance time in unit tests for token bucket refill cycles.  
* `FakeRateLimiter` : Emulate over-subscription and test fallback logic in your training harness.  
* `rate_limiter_fixture` : PyTest fixtures to spin up limiters with custom token rates.  
* `PriorityBucket` : Prioritize hyperparameter search jobs over less critical data-collection calls.  
* `TokenBucket` : Control refill_rate and bucket_capacity per model or tenant namespace.  
* `default_limits` decorator : Automatically enforce a baseline QPS on every inference endpoint.  
* `ThreadSafeLimiter` : Safe sharing of limiters across worker threads and RPC threads.  
* `@async_rate_limiter` : Rate-limit your asyncio-based inference pipeline or Trio data loaders.  
* `RateLimitLogger` : Structured events for every throttle decision, feeding into TensorBoard or Grafana.  
* `inspect_limiter()` : Programmatic introspection of current tokens, usage metrics, and next refill.  
* `whitelist_client` : Let core research teams bypass quotas during urgent debugging.  
* `burst_override()` : Temporary throughput boost for smoke tests or model warm-up.  
