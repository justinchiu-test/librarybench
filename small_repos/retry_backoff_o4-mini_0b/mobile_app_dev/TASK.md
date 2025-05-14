# The Task

I am a mobile app developer working on a chat application that relies on real-time presence and push notification services. I want a lightweight, pluggable retry library that handles flaky mobile network conditions, logs every backoff, and lets me configure strategies remotely. This repo offers a comprehensive retry toolkit I can integrate into my networking layer.

# The Requirements

* `BackoffRegistry` : Support runtime registration of custom mobile-friendly backoff strategies (e.g., signal-strength aware).  
* `ContextManagerAPI` : Use `with retry_context(...)` in async code or Rx chains to scope retryable network calls.  
* `OnRetryHook` : Trigger a callback before each actual sleep so I can show a “retrying…” indicator in the UI or record metrics.  
* `FullJitterBackoffStrategy` : Mitigate burst retries across thousands of clients by applying randomized jitter on exponential backoff.  
* `AfterAttemptHook` : Run a hook after each attempt to log success/failure counts and latency for in-app diagnostics.  
* `OnGiveUpHook` : Notify the user gracefully or log a fatal analytics event once all attempts are exhausted.  
* `ExponentialBackoffStrategy` : Offer a basic doubling-delay strategy for simple network operations.  
* `CircuitBreakerIntegration` : Fast-fail subsequent calls to avoid draining battery on constant retries when the server is down.  
* `MaxAttemptsStopCondition` : Enforce a strict maximum number of network retries to preserve device resources.  
* `EnvVarOverrides` : Remotely toggle or tune backoff parameters using environment variables injected at build or runtime.

