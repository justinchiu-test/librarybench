# The Task

I am an IoT Stream Analyst. I want to process millions of sensor readings per minute, detect anomalies, and deliver insights in near real time. This code repository provides a scalable, fault-tolerant stream processing toolkit with fine-grained control over resources and behavior.

# The Requirements

* `ErrorHandlingFallback` : Supply default sensor values when a node repeatedly times out.  
* `ErrorHandlingRetry` : Automatically retry transient network failures when ingesting edge data.  
* `ErrorHandlingSkip` : Skip malformed messages and log them for later inspection.  
* `JSONSerialization` : Convert device payloads into JSON for downstream dashboards.  
* `BackpressureControl` : Throttle device ingestion when analytics stages lag behind.  
* `DynamicReconfiguration` : Turn on/off anomaly-detection thresholds on the fly without stopping data flow.  
* `BuiltInBatch` : Batch telemetry into time-windows for efficient storage in TSDBs.  
* `BuiltInSort` : Reorder out-of-sequence readings based on timestamp.  
* `MemoryUsageControl` : Enforce per-stage memory caps, spilling to disk on bursts of data.  
* `Versioning` : Keep versions of pipeline specs for audit trails and experiment reproducibility.  
* `Windowing` : Apply sliding windows for moving-average temperature calculations.  
* `SamplingStage` : Randomly sample 1% of readings for quick sanity checks.  
* `BuiltInGroup` : Group readings by device type or location for batch enrichment.  
* `PipelineComposition` : Assemble multi-stage flows: intake → cleaning → anomaly detection → storage.  
* `BuiltInFilter` : Drop readings outside of expected physical ranges.  
* `BuiltInMap` : Convert raw bytes into structured telemetry objects.  
* `DataValidation` : Validate fields against a JSON Schema for each device model.  
* `SchemaEnforcement` : Enforce strict field presence, casting types or rejecting bad messages.  
* `PluginSystem` : Plug in new protocol adapters (e.g., CoAP, MQTT) without touching core code.  
* `CachingStage` : Cache recent device metadata for low-latency joins during enrichment.  
