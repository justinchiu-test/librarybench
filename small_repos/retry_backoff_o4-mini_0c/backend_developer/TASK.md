# The Task

I am a backend developer integrating external payment and notification APIs. I want to be able to handle intermittent service errors gracefully and collect diagnostics for debugging. This code repository offers a unified retry/backoff toolkit with extensibility and observability baked in.

# The Requirements

* `RetryHistoryCollector` : Log all retry attempts with delays, exceptions, and results for diagnostic dashboards.  
* `ConfigFileSupport` : Read retry thresholds, backoff profiles, and timeouts from JSON/TOML to align with our microservice configs.  
* `CircuitBreakerIntegration` : Automatically open and close circuits around flaky third‐party endpoints.  
* `StopConditionInterface` : Register custom stop logic, e.g. stop retrying if quota‐exhausted errors appear.  
* `CancellationPolicy` : Provide a way for other threads to cancel pending retries when a user request has already timed out.  
* `CLIUtilities` : Ship a CLI to simulate API failures and verify retry policies in CI pipelines.  
* `ContextManagerAPI` : Use `with retry_scope():` blocks around high‐risk calls to keep code clean.  
* `BackoffRegistry` : Let me plug in our proprietary jitter strategy at runtime without forking the code.  
* `TimeoutPerAttempt` : Enforce strict time budgets per attempt so we don’t hold worker threads indefinitely.  
* `AsyncIOIntegration` : Leverage async retry for our event‐driven notification service built on asyncio.  
