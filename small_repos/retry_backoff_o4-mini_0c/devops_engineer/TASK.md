# The Task

I am a DevOps engineer responsible for keeping our services resilient. I want to be able to centrally manage and observe retry and backoff policies so that transient failures don’t cascade into incidents. This code repository provides a comprehensive, configurable, and extensible retry/backoff framework that integrates with our toolchain and monitors.

# The Requirements

* `RetryHistoryCollector` : Record every attempt’s timestamp, delay, exception and outcome for alerting and post‐mortem analysis.  
* `ConfigFileSupport` : Load retry/backoff rules, thresholds and timeouts from YAML/JSON/TOML so ops teams can tune without code changes.  
* `CircuitBreakerIntegration` : Open the circuit to fast‐fail downstream calls when error rates exceed safe limits, then auto‐recover.  
* `StopConditionInterface` : Plug in custom stop conditions (e.g. total downtime budget, external health checks).  
* `CancellationPolicy` : Allow operations to be aborted via a thread‐safe `threading.Event` when deploys or scale‐downs occur.  
* `CLIUtilities` : Provide a CLI to validate policies against staging endpoints, simulate failures and generate reports.  
* `ContextManagerAPI` : Wrap blocks of service calls in a `with` statement to apply retry context and scoping.  
* `BackoffRegistry` : Dynamically discover or override backoff strategies (exponential, jittered, custom) via plugin entry points.  
* `TimeoutPerAttempt` : Impose hard timeouts on each try to avoid hung requests disrupting scheduler threads.  
* `AsyncIOIntegration` : Support `async` retry decorators and context managers for our asyncio‐based deployment scripts.  
