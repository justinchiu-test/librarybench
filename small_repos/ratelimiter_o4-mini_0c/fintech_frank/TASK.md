# The Task

I am a payments platform engineer in fintech. I want to be able to protect our transaction API from abuse while allowing VIP traders to burst during market volatility. This code repository ensures compliance, auditability, and predictable performance under load.

# The Requirements

* `MockableClock` : Simulate clock drift and leap-second scenarios in unit tests.  
* `FakeRateLimiter` : Create deterministic tests for scenarios like “limit hit” and “burst allowed.”  
* `rate_limiter_fixture` : Plug into CI pipelines so every pull request validates throttle policies.  
* `PriorityBucket` : Elevate market-making bots above normal retail traffic in times of stress.  
* `TokenBucket` : Regulate refill_rate and bucket_capacity to smooth out dips and spikes in request volumes.  
* `default_limits` decorator : Enforce safe defaults on payment endpoints even if a developer forgets to configure.  
* `ThreadSafeLimiter` : Guarantee correct token accounting when settlement threads and HTTP threads race.  
* `@async_rate_limiter` : Protect our async order-routing service built on asyncio.  
* `RateLimitLogger` : Produce auditable trails (JSON lines) of every blocked or served transaction.  
* `inspect_limiter()` : Dashboard integration to monitor real-time quotas and next refill times.  
* `whitelist_client` : Allow regulators and compliance scanners to bypass normal caps.  
* `burst_override()` : Permit short high-volume bursts for market-maker clients and then catch up.  
