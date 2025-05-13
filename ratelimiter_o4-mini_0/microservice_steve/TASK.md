# The Task

I am a microservices backend engineer building a high-scale API gateway. I want to be able to throttle, prioritize, and audit inbound calls so we never overwhelm downstream services. This code repository gives me a battle-tested rate-limiting library with everything I need for robust, observable traffic control.

# The Requirements

* `MockableClock` : Provide a fake, controllable clock for deterministic unit tests.  
* `FakeRateLimiter` : Simulate delays, rejections, and edge cases in CI without waiting on real time.  
* `rate_limiter_fixture` : Test fixture that injects preconfigured limiters into pytest or unittest suites.  
* `PriorityBucket` : Assign numeric priorities so emergency-path requests jump ahead of normal traffic.  
* `TokenBucket` : Classic token bucket implementation with adjustable refill_rate and capacity.  
* `default_limits` decorator : Apply per-function default throttle profiles without extra arguments.  
* `ThreadSafeLimiter` : Use fine-grained locks or lock-free queues so limiters work correctly under heavy threads.  
* `@async_rate_limiter` decorator : Async/await support for asyncio and Trio coroutines.  
* `RateLimitLogger` extension : Emit structured JSON or text logs for every allow/deny event.  
* `inspect_limiter()` : Query live token counts, usage stats, next available timestamp, and remaining quota.  
* `whitelist_client` : Static and dynamic allow-lists so internal health checks and trusted partners skip limits.  
* `burst_override()` : Temporarily boost capacity for high-priority operations, then auto-drain excess tokens.  
