# The Task

I am a real-time streaming platform engineer. I want to build data pipelines that can process high-velocity events without crashing or overloading memory. This code repository provides tools to compose and manage stages with backpressure, memory control, logging, metrics, retries/fallbacks, and dynamic reconfiguration.

# The Requirements

* `BackpressureControl` : Automatically throttle upstream sources when downstream stages are overwhelmed, preventing memory bloat.
* `MemoryUsageControl` : Monitor and limit memory consumption per stage, spilling to disk when thresholds are exceeded.
* `MonitoringMetrics` : Emit counters, timers, and gauges (records processed, error rates, latency) to monitoring backends like Prometheus.
* `RealTimeLogging` : Stream logs of processing events and errors directly to consoles or log aggregation services for immediate insight.
* `ErrorHandlingRetry` : Retry failed stages with a configurable backoff policy on transient errors.
* `ErrorHandlingFallback` : Provide fallback logic or default values when a stage repeatedly fails, preventing data loss.
* `DynamicReconfiguration` : Update pipeline topology and parameters at runtime without downtime, adapting to changing workloads and business rules.
