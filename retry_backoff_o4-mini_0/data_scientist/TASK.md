# The Task

I am a data scientist building an ETL pipeline that calls external APIs for enrichment. I want to gracefully handle transient failures, log each stage’s retry behavior, and experiment with different backoff strategies without changing code. This repository provides a modular retry engine I can configure on the fly.

# The Requirements

* `BackoffRegistry` : Dynamically discover and register new backoff strategies (for instance, rate-limit aware backoffs) via plugins.  
* `ContextManagerAPI` : Wrap each API call block in `with retry_context(...)` so my notebooks and scripts remain clean.  
* `OnRetryHook` : Invoke a hook only when a retry is scheduled to increment counters in my ML monitoring dashboard.  
* `FullJitterBackoffStrategy` : Use full jitter to randomize delays and avoid synchronized retries when enriching in parallel.  
* `AfterAttemptHook` : Capture metadata after every attempt (successful or not) for audit trails in our data lineage system.  
* `OnGiveUpHook` : Execute a final hook when the pipeline gives up on an API, so I can switch to fallback data sources.  
* `ExponentialBackoffStrategy` : Quickly test a simple doubling delay strategy for low-volume enrichment tasks.  
* `CircuitBreakerIntegration` : Leverage a circuit breaker to bypass failing API calls and prevent wasted compute.  
* `MaxAttemptsStopCondition` : Stop retrying once the max attempts threshold is hit, ensuring pipeline step failures bubble up.  
* `EnvVarOverrides` : Tune all retry settings in staging or production via environment variables without code changes.

