# The Task

I am a data engineer building nightly ETL pipelines. I want to schedule data ingestion jobs that honor local timezone shifts, allow me to tweak cron expressions dynamically when upstream schemas change, and fire ad-hoc one-off tasks when we need backfills. This code repository gives me a pluggable, thread-safe scheduler with hooks for loading database connections, built-in jitter to avoid thundering herds, and a REST API so my orchestration layer can spawn or cancel jobs programmatically.

# The Requirements

* `enable_daylight_saving_support` : Keep daily 2:00 AM ET ingestion aligned even when DST starts or ends.
* `dynamic_reschedule` : Modify pipeline intervals or cron expressions via API when data volume spikes or sources go offline.
* `schedule_one_off_task` : Launch single-run backfill jobs at an arbitrary datetime or after receiving a manual trigger.
* `register_pre_post_hooks` : Run pre-job data validation and post-job metadata registration.
* `apply_jitter_and_drift_correction` : Randomize start times by a few minutes and auto-correct any drift to prevent load spikes.
* `load_plugin` : Add custom serializers to write intermediate data to S3, Kafka, or proprietary stores.
* `create_task_group` : Group tasks per data domain (e.g., “user_events”, “sales”) to pause or resume entire pipelines.
* `ThreadSafeScheduler` : Ensure pipeline registrations and cancellations can happen concurrently from multiple worker threads.
* `emit_metrics` : Produce Prometheus metrics for job durations, success/failure counts, and schedule lag.
* `RESTfulManagementAPI` : Offer endpoints for our Airflow replacement to programmatically manage jobs.
