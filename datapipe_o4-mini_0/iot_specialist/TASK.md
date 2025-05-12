# The Task

I am an IoT specialist building a telemetry ingestion pipeline for thousands of sensors. I want reliable, low-latency data processing with windowed aggregates, HTTP-based control endpoints, and end-to-end schema validation. This repository simplifies building both batch reports and real-time dashboards, with metrics, retry logic, and pluggable serialization for embedded device data.

# The Requirements

* `increment_counter` : Count incoming device messages, parsed vs. dropped packets, thread-safe per device type.  
* `skip_on_error` : Skip corrupted or out-of-range sensor readings, log device IDs for manual review.  
* `run_batch` : Produce hourly summaries of sensor health and send daily maintenance reports.  
* `cli_manager` : CLI tool to register new devices, run manual backfills, and trace live streams.  
* `windowed_operations` : Compute tumbling windows for per-minute and sliding windows for complex event detection.  
* `http_adapter` : Pull firmware configs or push alerts via REST endpoints with retry/backoff.  
* `validate_schema` : Enforce custom JSON or binary schema for diverse sensor models to prevent data loss.  
* `register_serializer` : Integrate Protobuf or CBOR serializers for compact device telemetry formats.  
* `export_prometheus_metrics` : Expose device ingestion rates, latencies, and error ratios for monitoring.  
* `run_streaming` : Continuously ingest MQTT or WebSocket telemetry streams in real time.  
