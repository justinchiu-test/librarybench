# The Task

I am a compliance officer overseeing financial data pipelines. I want full visibility into every record’s transformation path, quick error strategies, and precise event-time handling. This code base gives me lineage, watermarks, and failsafe modes to meet audit requirements.

# The Requirements

* `tumbling_window()`        : Group transactions into audit windows for periodic compliance checks.  
* `sliding_window()`        : Produce rolling risk metrics over overlapping time intervals.  
* `add_serializer()`        : Register Avro or Parquet serializers to standardize ledger formats.  
* `throttle_upstream()`      : Enable backpressure so overloaded validation stages signal upstream to slow.  
* `watermark_event_time()`  : Use watermarks to tag late filings and control cutoff times accurately.  
* `halt_on_error()`         : Immediately halt on any unhandled exception to prevent non-compliant data flow.  
* `skip_error()`            : Optionally skip minor format violations with a logged warning to maintain throughput.  
* `setup_logging()`         : Integrate with `logging` to capture compliance-relevant events and errors.  
* `cli_manage()`            : Provide a CLI for triggering ad-hoc audits, reviewing logs, and deploying rules.  
* `parallelize_stages()`    : Execute validation, transformation and reporting stages in parallel for speed.  
* `track_lineage()`         : Record per-record lineage so I can trace exactly how each field was derived.  
