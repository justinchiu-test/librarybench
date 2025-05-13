# The Task

I am a Python Async Developer working on a high‐throughput event processing pipeline. I want to leverage asyncio/Trio idioms for rate limiting, plug in custom logging, and have my pipeline stay safe when the central Redis cluster is unreachable. This code repository gives me async‐first primitives plus policy hooks and durable state management.

# The Requirements

* `log_event`                : Async extension points for structured logging (JSON, text) of every rate decision.  
* `chain_policies`           : Parallel or sequential composition of token buckets and sliding windows.  
* `validate_config`          : Runtime validation of rate limit schemas before building async policies.  
* `get_runtime_metrics`      : Async methods to inspect live token counts, usage stats, next refill times, quotas.  
* `select_window_algo`       : Out‐of‐the‐box sliding, fixed, rolling window rate calculators and bucket types.  
* `enable_fault_tolerant`    : Fallback to local in‐memory limiting when Redis/tricache is unreachable.  
* `assign_priority_bucket`   : Tag tasks with priority buckets so critical events bypass lower‐priority traffic.  
* `persist_bucket_state`     : Async checkpointing of bucket state to disk or database for crash‐safe recovery.  
* `override_burst_capacity`  : High‐priority short bursts beyond nominal limits, with automated catch‐up drains.  
* `@async_rate_limiter`      : Decorators and async context managers for both asyncio and Trio.  
