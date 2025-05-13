# The Task

I am a DevOps/SRE responsible for our platform’s service mesh. I want to be able to configure, inspect, and evolve rate-limit policies without redeploying code. This code repository integrates with our control plane and monitoring stack.

# The Requirements

* `MockableClock` : Override time in end-to-end tests of our mesh policies.  
* `FakeRateLimiter` : Test backpressure strategies without spinning up hundreds of pods.  
* `rate_limiter_fixture` : Library-level fixtures for Terraform-driven integration tests.  
* `PriorityBucket` : Tag critical health-check traffic so services never go “red.”  
* `TokenBucket` : Fine-tune refill_rate and capacity parameters for each service.  
* `default_limits` decorator : Preload sane defaults for internal tools and dashboards.  
* `ThreadSafeLimiter` : Ensure global limiters in shared libraries behave under multi-threaded agents.  
* `@async_rate_limiter` : Support both asyncio-based controllers and Trio-powered operators.  
* `RateLimitLogger` : Hook into Fluentd/ELK for real-time alerting on denied requests.  
* `inspect_limiter()` : Query quota usage via CLI or REST for on-call troubleshooting.  
* `whitelist_client` : Dynamically add new services to allow-list when rotating credentials.  
* `burst_override()` : Enable controlled bursts for periodic backup or canary waves.  
