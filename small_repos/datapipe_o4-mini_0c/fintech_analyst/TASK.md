# The Task

I am a fintech analyst designing a pipeline to process high-volume market data and transactions. I need to validate schemas, handle spikes with windowed aggregates, backfill historical trades, and offer real-time alerts. This code repository provides end-to-end tooling for batch and streaming, pluggable formats, HTTP adapters for price feeds, and metrics for SLA dashboards.

# The Requirements

* `increment_counter` : Keep track of processed ticks, successful trades, and failed validations with thread-safe counters.  
* `skip_on_error` : Drop or quarantine bad trade records, log anomalies, and continue processing.  
* `run_batch` : Perform nightly reconciliation of daily trades with start/end audit logs.  
* `cli_manager` : CLI commands to bootstrap new market feeds, run backfills, and inspect pipeline status.  
* `windowed_operations` : Build sliding windows for VWAP and tumbling windows for candlestick generation.  
* `http_adapter` : Fetch live price quotes or submit aggregated data to RESTful endpoints with retries.  
* `validate_schema` : Validate incoming FIX-JSON or plain JSON messages against strict financial schemas.  
* `register_serializer` : Support Parquet for historical archiving and Avro for streaming downstream.  
* `export_prometheus_metrics` : Publish latency, throughput, and SLA breaches to Prometheus.  
* `run_streaming` : Process live market feeds continuously with sub-millisecond latencies.  
