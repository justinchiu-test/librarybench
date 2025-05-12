# The Task

I am a real-time streaming analyst building event‐driven dashboards. I want to continuously ingest, transform, and aggregate clickstream and sensor data, handle bad messages gracefully, and feed metrics into Grafana. This repository gives me a simple CLI, a true streaming engine, error strategies, built-in counters, rate limiting to protect our BI cluster, and Prometheus hooks for end-to-end visibility.

# The Requirements

* `scaffold_pipeline`     : Quick CLI scaffolding of event pipelines and transforms  
* `run_pipeline --stream` : Start a low-latency, streaming execution that processes records as they arrive  
* `monitor_pipeline`      : Live view of per-stage counters and error rates  
* `debug_pipeline`        : Drop into an interactive shell on failure to inspect record state  
* `enable_streaming`      : Consume unbounded streams from Kafka, MQTT, or HTTP sources  
* `set_skip_on_error`     : Continue past corrupt JSON or schema violations, logging warnings  
* `create_counter`        : Count hits, misses, aggregates, and exceptions in real time  
* `set_rate_limit`        : Cap emission at 1,000 RPS to upstream services  
* `start_prometheus_exporter`: Publish metrics to Prometheus for Grafana dashboards  
* `Processor` base class   : Encapsulate sliding‐window and stateful transforms in custom classes  
* `validate_schema`       : Drop or route events that do not adhere to our JSON Schema  
* `retry_on_error`        : Auto-retry transient failures (e.g., network blips) with exponential backoff  
* `halt_on_error`         : Fail fast on unexpected exceptions to prevent data skew  

