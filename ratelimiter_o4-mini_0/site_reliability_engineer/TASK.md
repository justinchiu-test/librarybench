# The Task

I am a Site Reliability Engineer tasked with maintaining SLAs for a distributed system. I want centralized observability into rate limiting, automated policy composition for new tenants, and fault‐tolerant behavior so the system never overloads during a datastore outage. This code repository offers me pluggable modules to meet all those demands.

# The Requirements

* `log_event`                : Emit structured logs and audit trails for every throttle or allow decision.  
* `chain_policies`           : Compose token-bucket, fixed-window, and custom policies in series or parallel.  
* `validate_config`          : Enforce schemas on YAML/JSON rate-limit files before enabling them.  
* `get_runtime_metrics`      : API to fetch current bucket levels, historical usage, and time to next refill.  
* `select_window_algo`       : Support sliding, fixed, rolling windows, plus token and leaky buckets.  
* `enable_fault_tolerant`    : Seamlessly switch to local in-memory counters if the external store is down.  
* `assign_priority_bucket`   : Define priority tiers so critical background jobs can preempt user traffic.  
* `persist_bucket_state`     : Periodically checkpoint in-memory counters to durable storage for recovery.  
* `override_burst_capacity`  : Configure short bursts above the nominal rate for time-sensitive ops.  
* `@async_rate_limiter`      : Provide async context managers and decorators for asyncio and Trio based scripts.  
