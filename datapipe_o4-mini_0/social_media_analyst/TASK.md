# The Task

I am a social media analyst building a real-time sentiment analysis pipeline. I want to handle out-of-order posts, enrich with NLP models, serialize results to Parquet or JSON, and recover gracefully from errors. This toolkit gives me a full streaming solution.

# The Requirements

* `tumbling_window()`        : Batch posts into minute-based tumbling windows for sentiment overviews.  
* `sliding_window()`        : Compute moving sentiment averages over a sliding five-minute window.  
* `add_serializer()`        : Plug in JSON, Avro or Parquet adapters for downstream storage.  
* `throttle_upstream()`      : Apply backpressure when the NLP enrichment stage lags behind.  
* `watermark_event_time()`  : Assign event-time watermarks to properly include late tweets.  
* `halt_on_error()`         : Immediately stop on critical model failures to prevent bad insights.  
* `skip_error()`            : Skip malformed posts or encoding errors and log a minor warning.  
* `setup_logging()`         : Use Python’s `logging` for debug info and error tracking.  
* `cli_manage()`            : Use the CLI to spin up new sentiment pipelines, monitor throughput, and tail logs.  
* `parallelize_stages()`    : Run ingestion, enrichment and aggregation in parallel processes for maximum throughput.  
* `track_lineage()`         : Maintain per-record lineage so I can audit exactly which models and filters processed each text.  
