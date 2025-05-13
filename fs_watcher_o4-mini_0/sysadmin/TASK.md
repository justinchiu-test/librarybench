# The Task

I am a system administrator tasked with monitoring log directories across multiple servers for security and compliance. I want a resilient file watcher that can exclude whitelisted files, throttle log‐flooding during attacks, and aggregate events into batches for downstream SIEM ingestion. This code repository is my toolbox for building an enterprise‐grade log watcher.

# The Requirements

* `configure_thread_pool(pool_size)` : Dispatch handlers for each monitored directory concurrently without exhausting system resources.
* `set_filters(include=['/var/log/**/*.log'], exclude=['/var/log/**/*.old','/var/log/debug/'])` : Only monitor active logs and ignore archived or debug files.
* `set_throttle(events_per_sec=100)` : Throttle flood of log rotations or attack‐triggered events.
* `on_event(forward_to_siem)` : Emit typed events (created/modified/deleted/moved) with timestamp and path.
* `batch_dispatch(batch_interval_ms=500)` : Group log events into batches to reduce SIEM API calls.
* `configure_logging(level='WARNING')` : Integrate with Python logging for warnings and errors when things go wrong.
* `set_polling_strategy(inotify_wrapper)` : Use an optimized polling or inotify‐based strategy depending on the host kernel.
* `apply_rate_limit('siem_submitter', 20)` : Limit throughput to the SIEM to prevent API throttling.
* `run_single_scan('/var/log/')` : Perform a manual scan to catch any missed logs during downtime.
* Context Manager API (`with fs_watcher.Watcher(config) as log_watcher:`) : Cleanly start and stop watchers in my cron jobs or daemons.
