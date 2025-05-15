# The Task

I am an IoT engineer building a sensor data aggregator for a smart-factory. I want to collect high-frequency sensor readings, compute metrics in windows, handle late or corrupt messages gracefully, and produce audit trails. This repository provides a modular streaming API with everything I need.

# The Requirements

* `tumbling_window()`        : Batch sensor readings into time-based windows for per-machine throughput stats.  
* `sliding_window()`        : Generate rolling averages and anomaly scores over sliding windows.  
* `add_serializer()`        : Swap in Protobuf or Parquet adapters to encode/decode sensor payloads.  
* `throttle_upstream()`      : Apply backpressure to slow data ingestion if the enrichment stage is overloaded.  
* `watermark_event_time()`  : Assign event-time watermarks so late telemetry is still processed in the correct window.  
* `halt_on_error()`         : Stop the entire pipeline on any unhandled exception to avoid propagating bad data.  
* `skip_error()`            : Skip corrupted sensor packets and log a warning so healthy data keeps flowing.  
* `setup_logging()`         : Hook into the Python `logging` module for centralized debug/info/warning messages.  
* `cli_manage()`            : Use the CLI to scaffold new sensor pipelines, start/stop jobs and query health checks.  
* `parallelize_stages()`    : Run ingestion, enrichment and storage stages in separate worker processes for throughput.  
