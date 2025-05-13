# The Task

I am a security analyst monitoring sensitive configuration files and log repositories for unauthorized changes. I need a secure, auditable watcher that labels each event, rate-limits alert floods, retries alerts on failures, and records a daily tamper-report. This code repository offers typed audit events, priority handlers, and summary reports for compliance.

# The Requirements

* `watch_directory(sensitive_paths)` : Emit structured audit events for created, modified, deleted, or moved files, including timestamps and absolute paths.
* `register_callback(path_regex, alert_handler, priority=100)` : Fire high-priority alerts for critical paths before lower-priority logging.
* `unregister_callback(handler_id)` : Dynamically adjust monitoring scope during investigations.
* `set_polling_strategy(audit_poller)` : Use high-frequency, secure polling hooks for Linux auditd or Windows audit logs.
* `configure_logging(logger=security_logger, level=logging.WARNING)` : Integrate with central SIEM logging at WARNING or above.
* `configure_rate_limit(alert_handler, max_events_per_minute=5)` : Prevent alert storms in case of mass chown or log rotations.
* `generate_change_summary('daily')` : Produce a tamper summary: “3 unauthorized moves, 2 deletions detected.”
* `get_async_watcher(loop)` : Allow asynchronous alert dispatch to our security orchestration platform.
* `single_scan(config_dir)` : Run an on-demand scan to baseline file integrity checks during audits.
* `set_retry_policy(max_retries=3, backoff_strategy='exponential')` : Retry failed alert deliveries to ensure no missed warnings.

