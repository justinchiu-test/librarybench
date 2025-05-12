# The Task

I am an ML researcher prototyping real-time feature extraction for a recommendation system. I want to be able to process clickstreams and user events in both batch (for model retraining) and streaming (for live scoring) modes, with robust error handling and full observability. This code repository provides modular building blocks for metrics, windowing, HTTP enrichment, schema checks, and flexible serialization.

# The Requirements

* `increment_counter` : Keep track of records ingested, enriched, and scored for experiment analysis, thread-safe.  
* `skip_on_error` : Drop bad feature vectors, log warnings, and keep the pipeline running.  
* `run_batch` : Trigger nightly feature engineering jobs over historical data with notifications.  
* `cli_manager` : Quickly scaffold new experiments, run pipelines locally, and debug with verbose flags.  
* `windowed_operations` : Build sliding windows for computing time-lagged features such as session counts.  
* `http_adapter` : Enrich event streams by calling external user profile services with retry logic.  
* `validate_schema` : Enforce JSON Schema for event formats to avoid downstream model corruption.  
* `register_serializer` : Serialize feature sets to Parquet or Avro for consumption by training pipelines.  
* `export_prometheus_metrics` : Monitor feature pipeline throughput and latency in Prometheus.  
* `run_streaming` : Continuously process live user events to generate real-time features for the recommender.  
