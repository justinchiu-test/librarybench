# The Task

I am a QA engineer designing tests for retry and backoff policies in staging environments. I want to be able to simulate failures, validate configurations, and capture detailed logs of each attempt. This code repository provides CLI tools, hooks, and interfaces to rigorously test our retry strategies before release.

# The Requirements

* `RetryHistoryCollector` : Gather full attempt histories so tests can assert on exact retry sequences.  
* `ConfigFileSupport` : Load test scenarios from JSON/YAML config files describing various backoff settings.  
* `CircuitBreakerIntegration` : Toggle circuit‐breaker behavior in tests to verify both open/closed paths.  
* `StopConditionInterface` : Inject custom stop conditions in test harnesses to simulate manual aborts.  
* `CancellationPolicy` : Trigger and validate thread‐safe cancellation via `threading.Event` in multi‐threaded tests.  
* `CLIUtilities` : Use the provided CLI to run parameterized retry tests against mock endpoints and generate pass/fail reports.  
* `ContextManagerAPI` : Write concise test cases using `with retry_test_scope():` for scoped retry behavior.  
* `BackoffRegistry` : Register dummy backoff functions in tests to speed up or slow down retries as needed.  
* `TimeoutPerAttempt` : Validate that timeouts per attempt are enforced and exceptions raised correctly.  
* `AsyncIOIntegration` : Test async retry logic in our asyncio‐based mock services using async decorators and context managers.  
