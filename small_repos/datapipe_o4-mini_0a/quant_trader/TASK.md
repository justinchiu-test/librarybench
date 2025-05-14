# The Task

I am a quantitative trader building a real-time signal generation engine. I want to be able to ingest tick data, run sliding and tumbling window aggregations, serialize to different formats for persistence, and gracefully handle late or malformed events without losing state. This code repository gives me a battle-tested streaming framework with pluggable modules for all of that.

# The Requirements

* `tumbling_window()`        : Batch tick records into tumbling windows of fixed time or count for OHLCV calculations.  
* `sliding_window()`        : Perform rolling aggregates over overlapping windows for momentum indicators.  
* `add_serializer()`        : Plug in Avro, Parquet or Protobuf serializers/deserializers for downstream storage.  
* `throttle_upstream()`      : Enable backpressure so that if my ML scoring stage lags, upstream data rates slow down automatically.  
* `watermark_event_time()`  : Define event-time watermarks to correctly handle out-of-order market ticks.  
* `halt_on_error()`         : Immediately stop the strategy on the first unhandled exception to avoid corrupted positions.  
* `skip_error()`            : Silently drop malformed price records (with optional warning) and continue live trading.  
* `setup_logging()`         : Integrate with Python’s `logging` module for TRACE, DEBUG, INFO and ERROR logs across components.  
* `cli_manage()`            : Use a CLI tool to scaffold new strategies, launch live pipelines and inspect runtime metrics.  
* `parallelize_stages()`    : Execute independent pipeline stages (ingest, enrich, score) in parallel processes to leverage multiple cores.  
