# The Task

I am a systems administrator responsible for automating routine maintenance and patching. I want to be able to schedule cron-like jobs that adapt automatically to DST changes, adjust running schedules on the fly when a critical patch window shifts, and group related jobs per environment (e.g., “prod” vs “staging”) so I can pause or cancel them all at once. This code repository gives me a robust scheduler with hooks for setting up environment variables, Prometheus metrics for monitoring job health, and a RESTful API for integration with our internal portal.

# The Requirements

* `enable_daylight_saving_support` : Automatically adjust maintenance windows across DST transitions to keep local times consistent.
* `dynamic_reschedule` : Change a job’s interval or cron expression at runtime via API call or CLI.
* `schedule_one_off_task` : Define one-time patch or reboot tasks by datetime or after a specified delay.
* `register_pre_post_hooks` : Insert custom pre-patch environment setup and post-patch cleanup logic.
* `apply_jitter_and_drift_correction` : Add random jitter to distributed maintenance jobs and auto-correct any schedule drift.
* `load_plugin` : Extend the scheduler with custom transport plugins to integrate with our proprietary alerting system.
* `create_task_group` : Organize jobs into “prod”, “staging”, and “dev” groups to apply bulk operations like pause-all or cancel-all.
* `ThreadSafeScheduler` : Use an internal loop safe for concurrent job registrations, cancellations, and state changes across threads.
* `emit_metrics` : Emit Prometheus-style counters and histograms for job runs, failures, and latencies to our monitoring stack.
* `RESTfulManagementAPI` : Expose endpoints to create, update, delete, and inspect scheduled jobs from our self-service dashboard.
