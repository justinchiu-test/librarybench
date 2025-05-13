# The Task

I am a FinTech Data Engineer. I want to build resilient, real-time transaction processing pipelines that can adapt to sudden load spikes and schema changes. This code repository gives me a modular, high-throughput framework with built-in safety nets and runtime agility.

# The Requirements

* `ErrorHandlingFallback` : Provide fallback logic or default values when a stage repeatedly fails.  
* `ErrorHandlingRetry` : Retry failed records or stages a configurable number of times before marking them as failed.  
* `ErrorHandlingSkip` : On stage failure, skip the faulty record and continue, with optional logging of error details.  
* `JSONSerialization` : Serialize and deserialize records to/from JSON for external audit logs and downstream APIs.  
* `BackpressureControl` : Automatically throttle upstream sources when downstream stages are overwhelmed, preventing memory bloat during market surges.  
* `DynamicReconfiguration` : Modify pipeline topology or stage parameters at runtime (e.g., switch fraud-detection thresholds) without downtime.  
* `BuiltInBatch` : Batch incoming transactions into fixed-size or time-based groups for efficient ledger commits.  
* `BuiltInSort` : Sort records by timestamp or transaction ID to guarantee in-order processing.  
* `MemoryUsageControl` : Monitor and limit memory consumption per stage, spilling to disk when thresholds are exceeded during heavy trading hours.  
* `Versioning` : Manage multiple versions of pipeline definitions and stage configurations for auditing and rollback after regulatory changes.  
* `Windowing` : Support sliding, tumbling, and session windows for time-based aggregations like rolling risk metrics.  
* `SamplingStage` : Extract random or stratified samples from live streams for integrity checks in test environments.  
* `BuiltInGroup` : Group records by account or region, emitting aggregated summaries for daily reconciliation.  
* `PipelineComposition` : Compose pipelines from reusable stage definitions—e.g., a generic cleansing sub-pipeline for all data sources.  
* `BuiltInFilter` : Filter out transactions below a fraud-risk threshold or exclude known test accounts.  
* `BuiltInMap` : Transform raw transaction fields into normalized financial objects.  
* `DataValidation` : Validate input records against business rules or JSON Schema, quarantining suspicious entries.  
* `SchemaEnforcement` : Enforce strict schema adherence, automatically casting or rejecting non-conforming fields after API version upgrades.  
* `PluginSystem` : Add custom connectors (e.g., to a proprietary clearinghouse) or new serialization formats via plugins.  
* `CachingStage` : Cache recent FX rates or customer profiles to speed up enrichment joins.  
