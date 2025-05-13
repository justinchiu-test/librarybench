# The Task

I am an API Backend Developer building a public REST API that must enforce quotas per user and per endpoint. I want to compose various rate‐limit strategies, instrument every decision for metrics, and ensure failsafe local limiting if Redis or Cassandra is down. This code repository helps me integrate and customize limits with minimal effort.

# The Requirements

* `log_event`                : Hook into structured JSON/text logs for every rate‐limit decision and user action.  
* `chain_policies`           : Chain a fixed‐window for global quotas with a token bucket for per‐endpoint bursts.  
* `validate_config`          : Perform schema enforcement on rate‐limit definitions at service startup.  
* `get_runtime_metrics`      : Query real‐time stats—tokens used, tokens left, next refill—for dashboards.  
* `select_window_algo`       : Choose between sliding, rolling, or fixed windows, plus leaky‐bucket smoothing.  
* `enable_fault_tolerant`    : Automatically fall back to in‐process rate limiting if external store is unreachable.  
* `assign_priority_bucket`   : Give premium and trial users different priority buckets to insulate paying customers.  
* `persist_bucket_state`     : Snapshot state every minute to a Postgres table to survive rolling deploys.  
* `override_burst_capacity`  : Permit occasional bursts for high‐value operations, then throttle back.  
* `@async_rate_limiter`      : Use async decorators in our FastAPI endpoints and Trio‐based microservices.  
