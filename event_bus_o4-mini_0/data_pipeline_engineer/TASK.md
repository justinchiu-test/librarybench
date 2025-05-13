# The Task

I am a data pipeline engineer orchestrating ETL jobs and event streams.  
I want to debounce, retry, and dead‐letter bad records, while being able to replay or audit every step.  
This code repository gives me a lightweight, testable event bus with transactional, delayed, filtered, and loggable features.

# The Requirements

* `subscribe(handler)`                : Hook into raw ingestion, transformation, and load stages synchronously.  
* `subscribe_once(handler)`           : Trigger schema validation or watermark updates just once per batch.  
* `unsubscribe(subscription_handle)`  : Shut off specific data flows or adapters on the fly.  
* `set_global_error_handler(fn)`      : Centralize exception handling across all pipeline stages.  
* `on_error(handler, error_callback)` : Implement per-stage retry logic or dead-lettering strategies.  
* `dead_letter_queue("bad_records")`  : Isolate records that fail after N retries into a “bad_records” DLQ.  
* `publish_delayed(event, delay_secs)`: Buffer spikes by scheduling back-pressure or rate-limiting events.  
* `with_transaction()`                : Stage multiple transformations and only commit publish if all succeed.  
* `add_filter(lambda e: e.value is not None)` : Drop null or invalid records before heavy processing.  
* `attach_logger(pipeline_logger)`    : Capture publishes, deliveries, errors, and subscription changes for audit trails.  
* `context_middleware()`              : Carry batch IDs, source file names, and correlation IDs through each handler.  
