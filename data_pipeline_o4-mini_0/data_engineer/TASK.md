# The Task

I am a Data Engineer. I want to be able to build a resilient, high-throughput ETL pipeline that can be monitored, reconfigured on the fly, and extended by plugging in new connectors or processing stages. This code repository provides a modular, production-ready data pipeline framework with built-in support for metrics, serialization, error handling, backpressure, batching, and more.

# The Requirements

* `MonitoringMetrics`       : Emit counters, timers, and gauges (records processed, error rates, latency) to monitoring backends like Prometheus.  
* `RealTimeLogging`         : Stream structured logs for every stage in real time, with configurable log levels and formats.  
* `ParallelExecution`       : Process independent pipeline stages concurrently using threads or worker processes, with adjustable concurrency limits.  
* `Checkpointing`           : Persist state snapshots periodically to recover from failures without reprocessing the entire dataset.  
* `ErrorHandlingFallback`   : Supply default values or alternate logic when a stage repeatedly fails on certain records.  
* `JSONSerialization`       : Serialize and deserialize records in JSON for interoperability with downstream systems.  
* `YAMLSerialization`       : Use YAML for pipeline configuration and ad-hoc data edits, improving human readability and diff clarity.  
* `SourceSinkHooks`         : Register pre- and post-processing hooks on inputs and outputs to inject custom logic (authentication, enrichment).  
* `BuiltInBatch`            : Group records into fixed-size or time-windowed batches for efficient bulk writes and downstream optimizations.  
* `BuiltInSort`             : Sort incoming data by specified keys before batching or grouping to enforce ordering guarantees.  
* `BackpressureControl`     : Automatically throttle upstream producers when downstream stages are overwhelmed, preventing memory spikes.  
* `DynamicReconfiguration`  : Modify pipeline topology, resource allocations, or processing parameters at runtime without a restart.  
* `BuiltInGroup`            : Group records by one or more fields, emitting lists, iterators, or aggregate summaries.  
* `PipelineComposition`     : Compose smaller pipeline fragments into larger workflows, enabling reuse of common processing patterns.  
* `ErrorHandlingSkip`       : Skip invalid or problematic records on failure, log the incidents, and continue processing.  
* `ErrorHandlingRetry`      : Retry failed records a configurable number of times with back-off before applying fallback or skip logic.  
* `DataValidation`          : Validate schemas or business rules against incoming records, quarantining or dropping those that fail.  
* `SchemaEnforcement`       : Enforce field types, required keys, and default values according to a JSON Schema definition.  
* `PluginSystem`            : Load custom connectors, serializers, processors or sinks from external packages via a plugin registry.  
* `CachingStage`            : Cache intermediate results in memory or local disk for repeated lookups or deduplication.  

