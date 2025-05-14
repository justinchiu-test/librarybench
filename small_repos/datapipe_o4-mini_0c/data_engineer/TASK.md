# The Task

I am a data engineer in a fast-paced e-commerce platform. I want to be able to build and orchestrate data ingestion and transformation pipelines that handle billions of events per day, while ensuring reliability, observability, and low latency. This code repository is my swiss-army knife for both batch and streaming workloads, with built-in metrics, error handling, schema checks, pluggable formats, and monitoring integrations.

# The Requirements

* `increment_counter` : Track simple counters (processed, succeeded, failed) per stage with thread-safe increments for SLA reporting.  
* `skip_on_error` : Silently skip malformed or problematic records, log a warning, and continue without failing the whole job.  
* `run_batch` : Execute pipelines in discrete daily or hourly batches with start/end notifications and summary metrics.  
* `cli_manager` : Scaffold, run, monitor, and debug pipelines through a unified CLI interface.  
* `windowed_operations` : Group records into tumbling or sliding windows by time or count for aggregated metrics.  
* `http_adapter` : Fetch from external REST APIs or post results using `urllib`, with configurable headers, timeouts, and retries.  
* `validate_schema` : Validate incoming JSON payloads against JSON Schema or custom business rules, rejecting or routing invalid data.  
* `register_serializer` : Plug in custom serializers/deserializers (Avro, Parquet, Protobuf) via a simple adapter interface.  
* `export_prometheus_metrics` : Expose all counters and gauges over HTTP in Prometheus format for Grafana dashboards.  
* `run_streaming` : Run pipelines continuously on unbounded Kafka or MQTT streams, processing events in real time.  
