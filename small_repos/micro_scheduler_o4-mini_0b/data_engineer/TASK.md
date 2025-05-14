# The Task

I am a data engineer building an ETL pipeline. I want to be able to schedule and monitor recurring data extraction and transformation jobs, fail over gracefully on errors, and query job health and history. This code repository will act as the backbone of my micro-scheduler to run, coordinate, and observe my nightly batch jobs.

# The Requirements

* `expose_metrics()` : Export Prometheus‐compatible counters, gauges, and histograms for job runtime, failure counts, and end-to-end latency.  
* `schedule_recurring_job()` : Register ETL tasks to run at fixed intervals (e.g., every 4 hours) indefinitely or until cancelled.  
* `attach_logger()` : Plug into Python’s `logging` module or custom handlers to capture scheduler and job logs, including INFO and ERROR level details.  
* `list_jobs()` : Query registered ETL jobs, their next run times, last run status, execution count, and custom tags like “daily”, “customer_data”.  
* `coordinate_leader_election()` : Run multiple scheduler instances in HA mode, elect a leader or use distributed locks so only one host runs the ETL pipeline at a time.  
* `run_async_job()` : Support coroutine-based jobs to non-block on I/O bound transformations (e.g., streaming from Kafka).  
* `register_hook()` : Provide hooks for custom alerts (e.g., Slack, PagerDuty) or additional metrics on job start, success, and failure.  
* `graceful_shutdown()` : On SIGINT/SIGTERM, finish in-flight ETL tasks, persist state, then shut down within an optional timeout.  
* `persist_jobs()` : Use JSON or `shelve` to save job definitions and last run states on disk, allowing restart recovery after maintenance or crashes.  
* `adjust_interval()` : Dynamically tune the polling interval of a recurring job (e.g., increase frequency when backfills are pending) without unregistering it.  
