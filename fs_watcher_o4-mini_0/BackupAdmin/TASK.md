# The Task

I am a systems backup administrator ensuring that user home directories and application servers are consistently backed up. I want to detect file changes in near-real time, debounce rapid edits, and produce daily summary reports to validate backup completeness. This code repository gives me structured events, rate limiting, change summaries, and on-demand scans for periodic full backups.

# The Requirements

* `watch_directory(target_paths, recursive=True)` : Receive typed events for every create/modify/delete/move with timestamp and file path.
* `register_callback(filter_pattern, backup_handler, priority=10)` : Prioritize full-backup triggers over incremental backups.
* `unregister_callback(callback_id)` : Unsubscribe backup routines during maintenance windows.
* `set_polling_strategy(custom_polling_fn)` : Inject ZFS-specific scanning logic or adjust intervals for NFS mounts.
* `configure_logging(level=logging.INFO)` : Log every backup action at INFO, debug filesystem internals at DEBUG.
* `configure_rate_limit(handler_id=backup_handler, max_events_per_sec=2)` : Debounce rapid file edits to avoid backup thrashing.
* `generate_change_summary('midnight')` : Auto-generate “7 files backed up, 1 deleted” reports for compliance.
* `get_async_watcher()` : Integrate with our asyncio-based orchestrator to schedule jobs without threading.
* `single_scan(base_path)` : Kick off a full, on-demand snapshot for monthly archive.
* `set_retry_policy(max_retries=4, backoff_strategy='exponential')` : Retry backup handlers that fail due to transient network issues.

