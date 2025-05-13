# The Task

I am a fintech engineer orchestrating batch settlements, reconciliations, and compliance reports. I want jobs to run at local market close times across multiple timezones, support on-the-fly adjustments when regulatory windows change, and fire once-off compliance checks on demand. This code repository delivers a secure, plugin-friendly scheduler with pre/post hooks for transactional context, drift correction to meet SLAs, and a RESTful management API for our risk platform.

# The Requirements

* `enable_daylight_saving_support` : Automatically adjust settlement and report jobs to local market close times even when DST shifts.
* `dynamic_reschedule` : Update cron schedules or intervals at runtime to handle unexpected market holidays or extended trading hours.
* `schedule_one_off_task` : Trigger single-run audits or compliance reports at a specified timestamp or after urgent investigation requests.
* `register_pre_post_hooks` : Open database transactions before task execution and commit/rollback afterwards.
* `apply_jitter_and_drift_correction` : Randomly jitter start times within an SLA window and auto-correct any schedule drift.
* `load_plugin` : Plug in custom serializers for encrypted payloads and transports compliant with our secure messaging bus.
* `create_task_group` : Group tasks by business domain (e.g., “settlement”, “reconciliation”, “reporting”) to perform bulk state changes.
* `ThreadSafeScheduler` : Guarantee thread-safe task scheduling and cancellation in our high-availability settlement cluster.
* `emit_metrics` : Expose Prometheus-style counters and histograms for job success rates, latencies, and drift metrics to our SRE team.
* `RESTfulManagementAPI` : Offer secure REST endpoints for our risk management portal to manage scheduled financial workflows.
