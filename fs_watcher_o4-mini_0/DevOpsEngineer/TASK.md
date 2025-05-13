# The Task

I am a DevOps engineer responsible for keeping our CI/CD pipeline in sync with the latest artifacts and configuration files. I want to be able to detect and react to file changes—creations, modifications, deletions, and moves—across multiple environments in real time, enforcing rate limits and priorities so that build-critical steps run first and noisy logs don’t overwhelm the system. This code repository gives me a robust filesystem watcher with structured events, retry policies, and customizable polling so I can plug it seamlessly into our orchestration tooling.

# The Requirements

* `watch_directory(path, handlers…)` : Emit typed events (created, modified, deleted, moved) with timestamp and path metadata when files or directories change.
* `register_callback(pattern, handler, priority=0)` : Subscribe handlers to path patterns (glob or regex) with priority levels so critical callbacks fire before less important ones.
* `unregister_callback(handler_id)` : Unsubscribe handlers on demand when a service scales down or configuration changes.
* `set_polling_strategy(poller_func)` : Swap out or extend default polling logic for environment-specific optimizations (e.g., increased interval on network mounts).
* `configure_logging(level=logging.INFO)` : Integrate with Python’s logging module to adjust verbosity (DEBUG, INFO, WARNING, ERROR) per deployment stage.
* `configure_rate_limit(handler_id=None, path=None, max_events_per_sec=10)` : Enforce maximum event throughput per handler or per path to protect downstream systems from storms.
* `generate_change_summary(interval)` : Produce a human-readable report like “5 files modified, 2 created” for our daily audit emails.
* `get_async_watcher(loop=None)` : Provide an awaitable API so our asyncio-based deployment scripts can await file events without blocking.
* `single_scan(path)` : Run a one-time directory crawl for manual health checks or initial sync when spinning up new build agents.
* `set_retry_policy(max_retries=3, backoff_strategy='exponential')` : Catch handler exceptions, retry failed callbacks with backoff, and surface persistent errors to PagerDuty.

