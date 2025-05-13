# The Task

I am a real-time data pipeline engineer building an ETL service that responds to incoming CSV drops, JSON logs, and Avro snapshots. I want to be able to watch multiple landing zones, ingest new files as they land, handle spikes without losing data, and log every step with clear debug info. This code repository provides typed events, rate limiting, and asyncio support so my ingestion workers can dynamically scale.

# The Requirements

* `watch_directory(paths, recursive=True)` : Emit structured events for every new, modified, moved, or deleted file, including timestamps and absolute paths.
* `register_callback(pattern, handler, priority)` : Assign priorities to ingestion steps: e.g., schema-validator before data-loader.
* `unregister_callback(handler_id)` : Cleanly detach pipeline components during redeploys.
* `set_polling_strategy(custom_poller)` : Plug in HDFS, S3-fuse or optimized OS-specific polling modules.
* `configure_logging(logging.getLogger('pipeline'), level=logging.DEBUG)` : Integrate with the Python logging module for run-by-run verbosity control.
* `configure_rate_limit(path='*.csv', max_events_per_sec=5)` : Protect downstream storage by throttling event throughput per file type.
* `generate_change_summary(period='hourly')` : Autogenerate “12 CSVs ingested, 3 JSON logs moved” summary for dashboards.
* `get_async_watcher()` : Return an asyncio-based watcher so my coroutines can `await event_loop.create_task(watcher.next_event())`.
* `single_scan('/data/incoming')` : Trigger a one-time crawl before service startup to backfill missing data.
* `set_retry_policy(max_retries=5, backoff_strategy='linear')` : Retry transient failures (e.g., DB lock timeouts) with backoff.

