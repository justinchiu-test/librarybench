# The Task

I am a Marketing Data Scientist. I want to build ad-hoc and scheduled pipelines that aggregate multi-channel campaign data, apply complex business rules, and deliver clean datasets for reporting. This code repository offers a highly modular, schema-safe framework that scales from dev notebooks to production.

# The Requirements

* `ErrorHandlingFallback` : Fill missing campaign metrics with last-known values when data sources fail.  
* `ErrorHandlingRetry` : Retry flaky API calls to ad platforms or CRMs.  
* `ErrorHandlingSkip` : Skip bad records in clickstream logs and record them for audit.  
* `JSONSerialization` : Export final datasets as JSON for BI tools.  
* `BackpressureControl` : Slow down ETL pulls when transformations backlog.  
* `DynamicReconfiguration` : Update transformations or add new ad platform connectors on the fly.  
* `BuiltInBatch` : Batch click and impression events into hourly windows.  
* `BuiltInSort` : Sort events by timestamp to reconstruct customer journeys.  
* `MemoryUsageControl` : Limit in-memory aggregations, spilling to disk for very large campaigns.  
* `Versioning` : Track pipeline and schema versions for each report release.  
* `Windowing` : Use tumbling windows for daily spend summaries and sliding windows for rolling ROI.  
* `SamplingStage` : Sample sessions to validate data quality before full processing.  
* `BuiltInGroup` : Group events by user or campaign for multi-touch attribution.  
* `PipelineComposition` : Compose standard cleaning, join, and aggregation stages into reusable flows.  
* `BuiltInFilter` : Filter out internal IPs or bot traffic.  
* `BuiltInMap` : Map raw log fields into unified event models.  
* `DataValidation` : Validate campaign data against business rules or JSON Schema.  
* `SchemaEnforcement` : Enforce dataset schemas, casting fields or rejecting mismatches.  
* `PluginSystem` : Add connectors to new ad networks or data warehouses via plugins.  
* `CachingStage` : Cache lookup tables like geo-lookups or marketing taxonomies for enrichment.  
