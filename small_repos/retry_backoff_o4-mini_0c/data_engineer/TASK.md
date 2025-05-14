# The Task

I am a data engineer running asynchronous ETL pipelines that ingest from unreliable sources. I want to be able to orchestrate retries transparently, time out hung reads, and cancel stuck tasks when the pipeline is shut down. This code repository brings together sync/async retry, timeouts, cancellation and monitoring in one place.

# The Requirements

* `RetryHistoryCollector` : Capture per-attempt metadata so I can feed it into our monitoring and anomaly detection.  
* `ConfigFileSupport` : Drive pipeline retry & backoff settings from a central TOML config.  
* `CircuitBreakerIntegration` : Fast‐fail long‐failing connectors and auto‐heal when endpoints recover.  
* `StopConditionInterface` : Add custom stop conditions (e.g. message‐volume limits) to stop retries at scale.  
* `CancellationPolicy` : Allow pipeline orchestrator to signal an in‐flight task to cancel via a shared `Event`.  
* `CLIUtilities` : Include a CLI helper to stress‐test connector retry behavior before running daily jobs.  
* `ContextManagerAPI` : Wrap extraction logic in a `with retry_context():` for clean pipeline code.  
* `BackoffRegistry` : Dynamically register custom exponential plus random backoff strategies used in our workflows.  
* `TimeoutPerAttempt` : Ensure each stage of the ETL doesn’t exceed its allotted time slice.  
* `AsyncIOIntegration` : Use async retry/context‐manager blocks in our asyncio‐based streaming ingestion.  
