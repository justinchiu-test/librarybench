# The Task

I am an open‐source Python library author building a resilient HTTP client for users. I want to be able to expose rich retry/backoff customization while keeping defaults sane. This code repository delivers modular, pluggable components that let me offer end users a battle‐tested retry framework with minimal boilerplate.

# The Requirements

* `RetryHistoryCollector` : Expose a hook so library users can inspect attempt logs or attach custom metrics.  
* `ConfigFileSupport` : Offer optional config loading so clients can override behavior via project‐wide YAML/JSON/TOML.  
* `CircuitBreakerIntegration` : Integrate a safe fail‐fast circuit breaker that library users can configure or disable.  
* `StopConditionInterface` : Provide an interface so users can drop in their own stop condition implementations.  
* `CancellationPolicy` : Support external cancellation (e.g. user interrupts, cancel tokens) in a thread-safe manner.  
* `CLIUtilities` : Ship a utility script so users can test different retry settings against example endpoints.  
* `ContextManagerAPI` : Let users apply retry logic in a `with` block around arbitrary code sections.  
* `BackoffRegistry` : Auto-register built‐in and custom backoff functions via entry points for easy extension.  
* `TimeoutPerAttempt` : Allow library users to set per-request timeouts that raise on overrun.  
* `AsyncIOIntegration` : Offer `@async_retry` decorators and async context managers for asyncio‐based clients.  
