# The Task

I am a data pipeline engineer orchestrating ETL jobs that fetch from flaky external APIs.  
I want to be able to wrap each network call in retry logic with configurable backoff, jitter, and dynamic stop conditions, while logging attempt details and propagating pipeline metadata.  
This repository gives me a uniform API to instrument, monitor, and extend retry behavior, whether I’m running in bare Python scripts or inside an async I/O scheduler.

# The Requirements

* `FullJitterBackoffStrategy`  : Mixes exponential backoff with random jitter to prevent batch-job thundering.
* `BackoffGeneratorInterface`   : Allows me to implement a custom Fibonacci or polynomial backoff generator.
* `ContextPropagation`          : Ensures my pipeline’s run ID, data schema version, and other tags follow through every retry.
* `ExponentialBackoffStrategy`  : Basic doubling delay strategy with optional maximum wait time.
* `ContextManagerAPI`           : Enables `with retry_scope(...)` blocks around calls like `extract()`, `transform()`, `load()`.
* `OnRetryHook`                 : Lets me attach callbacks to send alerts or kick off compensating actions on each retry.
* `MetricsHook`                 : Hooks into Prometheus counters, Graphite gauges, or StatsD timers for retry counts and latencies.
* `AsyncIOIntegration`          : Async decorators and context managers so I can retry inside `async def` ETL tasks.
* `MaxAttemptsStopCondition`    : Stops the retry loop after N attempts to avoid infinite loops on persistent errors.
* `RetryHistoryCollector`       : Captures full attempt logs (time, backoff, exception) for post-mortem analysis.
