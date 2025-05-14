# The Task

I am an IoT edge operator deploying data pipelines on remote devices. I want rock-solid ingestion of sensor streams, local metrics for device health, configurable retries when connectivity drops, rate limiting to conserve bandwidth, and the ability to debug in the field. This repository gives me a portable CLI, streaming execution, error policies, counters, bandwidth controls, a Prometheus endpoint, and pluggable processors/validators.

# The Requirements

* `scaffold_pipeline`     : CLI to generate edge pipeline skeletons for new sensor networks  
* `run_pipeline --stream` : Run continuously on unbounded sensor readings  
* `monitor_pipeline`      : View local counters for packets processed, succeeded, failed  
* `debug_pipeline`        : Remote‐SSH into the pipeline for live debugging  
* `enable_streaming`      : Process data as it arrives from LoRaWAN, BLE, or CAN bus  
* `set_skip_on_error`     : Drop malformed sensor payloads silently, logging a warning  
* `create_counter`        : Safe counters for packet counts, error counts, uptime  
* `set_rate_limit`        : Limit packets sent upstream to conserve satellite or cellular bandwidth  
* `start_prometheus_exporter`: Host a local HTTP endpoint for Prometheus scrapes  
* `Processor` base class   : Write custom drivers and calibrations as classes implementing `process()`  
* `validate_schema`       : Enforce JSON Schema on telemetry payloads, route invalid records to local storage  
* `retry_on_error`        : Retry transient network or sensor read failures with exponential backoff  
* `halt_on_error`         : Shut down the pipeline on unrecoverable hardware exceptions  

