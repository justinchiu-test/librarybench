# The Task

I am a DevOps Engineer responsible for ensuring our microservices remain performant under unpredictable loads. I want to be able to deploy and operate a robust rate‐limiting service that adapts automatically when our distributed datastore goes down and provides automated audit trails for compliance. This code repository gives me the tools, extension hooks, and service modes I need to achieve that.

# The Requirements

* `log_event`                : Provide extension points for structured logging (JSON, text) of rate‐limit events and user actions.  
* `chain_policies`           : Combine multiple strategies (e.g., token bucket + fixed‐window) in sequence or parallel to handle a mix of bursty and steady traffic.  
* `validate_config`          : Validate user‐supplied limits and reject misconfigurations at startup to prevent silent failures.  
* `get_runtime_metrics`      : Expose methods to query current token counts, usage statistics, next‐available timestamps, and remaining quota.  
* `select_window_algo`       : Support sliding window, fixed window, and rolling window calculators alongside token/leaky buckets.  
* `enable_fault_tolerant`    : Gracefully degrade to local in‐memory limits when the distributed store is unreachable.  
* `assign_priority_bucket`   : Assign priority levels to tokens so that critical operations can bypass or preempt lower‐priority calls.  
* `persist_bucket_state`     : Periodically persist bucket state to disk or database for safe recovery after restarts.  
* `override_burst_capacity`  : Allow short‐lived bursts above nominal rate for high‐priority operations, with catch‐up drains.  
* `@async_rate_limiter`      : Provide async/await decorators and async context managers compatible with asyncio and Trio for new Python services.  
