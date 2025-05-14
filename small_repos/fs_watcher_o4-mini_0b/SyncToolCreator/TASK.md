# The Task

I am developing a cross-platform file sync tool that keeps two directories mirrored in near real time. I need granular events, rate-limiting to avoid infinite loops, retry logic for network glitches, custom polling for remote mounts, and change summary logs for end users. This code repository supplies all those features in a unified, easy-to-extend API.

# The Requirements

* `watch_directory(source_dir, recursive=True)` : Emit typed events (create, modify, delete, move) with file path and timestamp so I can reconcile two trees.
* `register_callback(event_pattern, sync_handler, priority=50)` : Prioritize local deletes or moves before remote sync pushes.
* `unregister_callback(callback_id)` : Detach sync handlers when user toggles sync off.
* `set_polling_strategy(network_poller)` : Swap in optimized polling logic for SSHFS, CIFS, or cloud-fuse mounts.
* `configure_logging(level=logging.DEBUG)` : Offer verbose debugging for end-user troubleshooting, info logs for normal use.
* `configure_rate_limit(sync_handler, max_events_per_sec=1)` : Throttle sync pushes to avoid loops or saturating network.
* `generate_change_summary(interval='every 30m')` : Show users “4 files updated, 3 renamed” in the UI.
* `get_async_watcher(loop)` : Expose an asyncio adapter so the GUI backend can await file events.
* `single_scan(dir_path)` : Provide a manual “re-sync now” action to the user for on-demand reconciliation.
* `set_retry_policy(max_retries=5, backoff_strategy='exponential')` : Retry failed remote writes or deletes with backoff.

