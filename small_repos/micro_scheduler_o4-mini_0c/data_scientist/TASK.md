# The Task

I am a Data Scientist building nightly ETL pipelines and model training workflows. I want to orchestrate data ingestion, transformation, training, and validation steps reliably, with full observability and fault‐tolerance. This code repository gives me a flexible scheduler to coordinate multi‐step experiments and recover cleanly from failures.

# The Requirements

* `graceful_shutdown` : Ensure long‐running data loads and model saves complete or roll back safely on shutdown signals.
* `health_check` : Query scheduler health via HTTP or CLI to integrate with monitoring dashboards and alerting.
* `trigger_job` : Rerun any pipeline stage on demand to debug or refresh data without waiting for the next schedule.
* `schedule_job` : Use cron expressions, interval, or start‐offset delays to kick off nightly jobs or hourly data syncs.
* `set_persistence_backend` : Store job metadata and intermediate state in Redis or a local SQLite file, depending on environment.
* `timezone_aware` : Handle different regional data sources by scheduling jobs in their local timezones, including DST.
* `exponential_backoff` : Automatically retry flaky data pulls from APIs with exponential backoff to avoid hammering endpoints.
* `define_dependencies` : Build a DAG so that ingestion → transformation → training → evaluation run in sequence.
* `retry_job` : Configure retries on training failures with custom backoff and maximum attempts.
* `limit_resources` : Restrict GPU‐intensive training jobs to one at a time and limit CPU‐bound ETL tasks concurrently.
