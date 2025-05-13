# The Task

I am a site reliability engineer tasked with hardening our microservices against transient faults.  
I want to be able to apply and tune retry policies across multiple services, collect consistent metrics, and preserve request context for tracing.  
This code base gives me all the tools—pluggable backoff, async/sync support, hooks, metrics, and history collection—to enforce SLO-compliant retry behaviors.

# The Requirements

* `FullJitterBackoffStrategy`  : Use randomized exponential backoff to smooth out retry traffic bursts.
* `BackoffGeneratorInterface`   : Swap in custom delay generators if our standard policies evolve.
* `ContextPropagation`          : Tag each retry with service- and request-level metadata for tracing.
* `ExponentialBackoffStrategy`  : A simple doubling delay strategy for low-risk operations.
* `ContextManagerAPI`           : Wrap critical calls inside `with retry_manager:` blocks for scoping.
* `OnRetryHook`                 : Trigger alerts or update dashboards only when an actual retry occurs.
* `MetricsHook`                 : Stream retry counts, latencies, and failures into our Prometheus stack.
* `AsyncIOIntegration`          : Support both synchronous handlers and `asyncio`-based endpoints.
* `MaxAttemptsStopCondition`    : Enforce a global cap on attempts to avoid endless retries in blackout scenarios.
* `RetryHistoryCollector`       : Persist detailed retry logs to ELK for post-incident review.
