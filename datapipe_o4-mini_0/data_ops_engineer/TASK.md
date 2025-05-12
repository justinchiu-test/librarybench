# The Task

I am a DataOps engineer responsible for building and maintaining robust data ingestion workflows. I want to be able to scaffold, run, monitor, and debug pipelines quickly while enforcing error‐handling policies, capturing metrics for SLAs, and exposing telemetry for our monitoring stack. This code repository provides a unified CLI, streaming and batch modes, flexible error strategies, built-in counters, rate limiting, Prometheus integration, and pluggable processors and validators.

# The Requirements

* `scaffold_pipeline`    : Provide a command‐line interface to scaffold new pipelines from templates  
* `run_pipeline`          : CLI command to launch pipelines in batch or streaming execution mode  
* `monitor_pipeline`      : CLI command to tail logs and view live metrics per stage  
* `debug_pipeline`        : CLI command to step through failures interactively  
* `enable_streaming`      : Switch to streaming execution to process unbounded data in real time  
* `set_skip_on_error`     : Silently skip malformed or problematic records (with warning logs) and continue  
* `create_counter`        : Thread‐safe counter abstraction to track processed/succeeded/failed records per stage  
* `set_rate_limit`        : Throttle record emission to a maximum records‐per‐second rate to protect downstream systems  
* `start_prometheus_exporter`: Expose all metrics over HTTP in Prometheus format for scraping  
* `Processor` base class   : Define class‐based processors with a common `process(record)` interface  
* `validate_schema`       : Validate incoming records against JSON Schema or custom rules, routing invalid data  
* `retry_on_error`        : Retry failed records up to a configurable limit (with optional backoff) before fallback  
* `halt_on_error`         : Immediately stop pipeline execution on the first unhandled exception  

