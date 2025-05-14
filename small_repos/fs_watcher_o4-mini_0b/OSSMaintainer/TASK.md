# The Task

I am an open-source library maintainer building a cross-platform FS watcher that “just works” on Linux, macOS, and Windows. I want contributors to easily swap in platform-specific polling strategies, hook into verbose logging, and test error-recovery without diving into complex internals. This code repository offers a clean, plugin-style API with typed events and async support.

# The Requirements

* `watch_directory(base_path, options=None)` : Emit typed events for file system changes with path and timestamp metadata in a portable format.
* `register_callback(glob_pattern, callback, priority=0)` : Let maintainers and users register handlers with priority ordering.
* `unregister_callback(callback_id)` : Remove handlers during module unload or tests.
* `set_polling_strategy(name, PollerClass)` : Allow plugin registration of inotify, fsevents, ReadDirectoryChangesW or pure-Python pollers.
* `configure_logging(logger=None, level=logging.WARNING)` : Tie into Python’s logging module and let end users adjust verbosity.
* `configure_rate_limit(max_events=100, per_second=True)` : Limit event floods on large repos or CI runs.
* `generate_change_summary(window='daily')` : Provide “X added, Y deleted, Z moved” stats in docs and release notes.
* `get_async_watcher(loop)` : Return an awaitable asyncio adapter for modern Python code.
* `single_scan(dirname)` : Expose a single, on-demand crawl for testing, health checks, or initial indexing.
* `set_retry_policy(retries=2, backoff='constant')` : Test handler error flows and retry logic easily in our test suite.

