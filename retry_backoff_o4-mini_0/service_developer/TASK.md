# The Task

I am a microservice developer building resilient HTTP clients.  
I want to be able to transparently retry transient failures in my REST calls—with exponential backoff, random jitter, metrics, hooks, and context propagation—without littering my business logic with sleep calls or boilerplate.  
This code repository provides decorators, context-managers, and plugin interfaces so that I can plug in new backoff strategies, capture rich retry diagnostics, and integrate seamlessly with both synchronous and asynchronous code paths.

# The Requirements

* `FullJitterBackoffStrategy`  : Combines exponential backoff with randomized jitter to mitigate thundering-herd issues.
* `BackoffGeneratorInterface`   : Pluggable interface to register entirely new backoff sequence generators.
* `ContextPropagation`          : Mechanism to carry user-defined context or metadata (e.g., request ID, tenant info) across all retry attempts.
* `ExponentialBackoffStrategy`  : Doubles the delay after each failed attempt up to an optional cap.
* `ContextManagerAPI`           : A `with`-block interface for scoping retry behavior around any block of code.
* `OnRetryHook`                 : Hook triggered only when a retry is actually scheduled (i.e., on failure and just before sleeping).
* `MetricsHook`                 : Built-in integration points for capturing retry and latency metrics (Prometheus, StatsD, etc.).
* `AsyncIOIntegration`          : Async decorator and context-manager variants compatible with `asyncio` event loops.
* `MaxAttemptsStopCondition`    : Halts retries once a defined maximum number of attempts has been reached.
* `RetryHistoryCollector`       : Records detailed attempt histories (timestamps, delays, exceptions, outcomes) for inspection or debugging.
