# The Task

I am an IoT integration specialist managing thousands of edge sensors that report telemetry to the cloud. I want a robust, configurable retry framework that handles intermittent connectivity, logs every attempt for auditing, and lets me swap strategies for different device classes without firmware updates. This library fulfills those needs.

# The Requirements

* `BackoffRegistry` : Dynamically load device-class-specific backoff strategies via plugin entry points.  
* `ContextManagerAPI` : Wrap sensor data transmission in `with retry_context(...)` blocks for clear, scoped retry logic.  
* `OnRetryHook` : Fire a hook only when a real retry is scheduled to update the edge device’s local status LED or log entry.  
* `FullJitterBackoffStrategy` : Use full jitter with exponential backoff to stagger retry transmissions from thousands of sensors.  
* `AfterAttemptHook` : Capture telemetry after every attempt—success or failure—for secure audit logs.  
* `OnGiveUpHook` : Trigger an onboard fallback (e.g., local storage flush) when retries are exhausted.  
* `ExponentialBackoffStrategy` : Provide a simple doubling-delay strategy for constrained devices.  
* `CircuitBreakerIntegration` : Integrate a circuit breaker to fast-fail and switch to offline mode under sustained failures.  
* `MaxAttemptsStopCondition` : Stop retries after the defined maximum attempts to conserve battery and bandwidth.  
* `EnvVarOverrides` : Override retry parameters via environment variables (or remote configuration) for zero-touch fleet tuning.  
