# The Task

I am an open-source maintainer of an async utilities library.  
I want to be able to offer end users a drop-in retry/backoff solution that works seamlessly in both sync and `asyncio` code, with full plugin support and detailed telemetry.  
This repository enables me to expose a consistent interface, where users can pick strategies, hook into events, and gather metrics or histories with minimal configuration.

# The Requirements

* `FullJitterBackoffStrategy`  : Provide a default “exponential + jitter” strategy for users out of the box.
* `BackoffGeneratorInterface`   : Let users register their own generators (Leaky bucket, linear).
* `ContextPropagation`          : Carry user context (like trace IDs) across coroutines and threads.
* `ExponentialBackoffStrategy`  : Include a standard doubling delay strategy with configurable cap.
* `ContextManagerAPI`           : Expose a `with retry:` API alongside decorators.
* `OnRetryHook`                 : Fire only when a retry is actually scheduled, so users can react programmatically.
* `MetricsHook`                 : Offer built-in hooks for Prometheus/StatsD to minimize user setup.
* `AsyncIOIntegration`          : Ensure decorators and context managers are `async`-friendly and compatible with event loops.
* `MaxAttemptsStopCondition`    : Default stop condition based on maximum attempts, with easy override.
* `RetryHistoryCollector`       : Collect per-attempt details for logging, debugging, or custom sinks.
