# The Task

I am a data engineer responsible for ingesting daily feeds from multiple distributed file shares. I want to be able to reliably detect new, modified, or deleted data files in real time without overwhelming my processing pipeline. This code repository provides a flexible, configurable file‐system watcher that integrates into my ETL workflows.

# The Requirements

* `configure_thread_pool()` : Use a configurable pool of worker threads to dispatch handlers concurrently without overloading the system.
* `set_filters(include_patterns, exclude_patterns)` : Support include and exclude filters (e.g., ingest only `*.csv`, ignore `*.tmp` and version-control directories).
* `set_throttle(rate_limit_per_sec)` : Apply a throttle mechanism to limit event delivery in high‐churn directories and avoid pipeline backlog.
* `on_event(callback)` : Emit typed events (`created`, `modified`, `deleted`, `moved`) with timestamp and path metadata to downstream processors.
* `batch_dispatch(interval_ms)` : Group multiple events into a single batch delivery at configurable intervals for efficiency.
* `configure_logging(level)` : Integrate with Python’s `logging` module, offering debug through error verbosity for audit trails.
* `set_polling_strategy(custom_strategy)` : Provide hooks to swap out or extend default polling logic for optimized scans on network‐mounted shares.
* `apply_rate_limit(handler_name, max_events_per_sec)` : Enforce maximum event throughput per handler or per path to protect downstream systems.
* `run_single_scan(path)` : Perform an on‐demand one‐time directory crawl for manual sync verification or health checks.
* `__enter__` and `__exit__` (Context Manager API) : Use `with fs_watcher.Watcher(...) as w:` for automatic setup and teardown of watchers. 
