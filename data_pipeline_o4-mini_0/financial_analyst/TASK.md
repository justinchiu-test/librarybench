# The Task

I am a Financial Analyst. I want to ingest, normalize, and aggregate streaming trades and market data in real time, triggering alerts on anomalies and generating periodic summaries for reports. This repo offers a flexible, observable, and resilient streaming‐batch framework I can tailor to my quant workflows.

# The Requirements

* `MonitoringMetrics`       : Count trades per symbol, compute latencies, and monitor error spikes in real time.  
* `RealTimeLogging`         : Capture detailed audit logs for each message transformation with timestamps.  
* `ParallelExecution`       : Fan-out symbol partition processing across worker threads to meet low-latency SLAs.  
* `Checkpointing`           : Persist stateful aggregates (VWAP, position counts) so recovery is immediate after any crash.  
* `ErrorHandlingFallback`   : On repeated feed failures, switch to backup data provider or emit default null values.  
* `JSONSerialization`       : Output consolidated trade tick data as JSON for BI dashboards.  
* `YAMLSerialization`       : Version pipeline configurations, alert rules, and threshold tables in YAML for peer review.  
* `SourceSinkHooks`         : Hook into Kafka or REST endpoints to ingest market data and publish alerts.  
* `BuiltInBatch`            : Batch trades into 1-second windows for OHLC and volume aggregation.  
* `BuiltInSort`             : Sort ticks by timestamp before batching to ensure correct window boundaries.  
* `BackpressureControl`     : Automatically throttle inbound message rate when compute lag exceeds thresholds.  
* `DynamicReconfiguration`  : Tune window sizes, alert thresholds, or add new metrics streams without downtime.  
* `BuiltInGroup`            : Group trades by symbol, emitting aggregated statistics per equity or derivative.  
* `PipelineComposition`     : Compose streams for equities, FX, and fixed income into a unified analytics workflow.  
* `ErrorHandlingSkip`       : Skip malformed market messages, log the raw payload for later forensic analysis.  
* `ErrorHandlingRetry`      : Retry transient API errors against data vendors up to configurable attempts.  
* `DataValidation`          : Validate message schemas against FIX or custom JSON schemas, quarantining invalid entries.  
* `SchemaEnforcement`       : Enforce numeric types, timestamp formats, and mandatory fields in incoming records.  
* `PluginSystem`            : Add custom alert modules, new data source adaptors, or proprietary model evaluators as plugins.  
* `CachingStage`            : Cache recent price ticks in memory to support low-latency anomaly detection.  
