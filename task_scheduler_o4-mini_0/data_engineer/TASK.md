# The Task

I am a Data Engineer building an ETL pipeline. I want to be able to react instantly to new data drops, kick off long‐running transformation jobs in isolation, and monitor everything in production. This code repository provides a flexible scheduler to orchestrate file ingestions, database writes, and downstream analytics tasks with full observability and fault tolerance.

# The Requirements

* `add_event_trigger`       : Fire tasks on external signals (e.g., new CSV in S3, filesystem changes, message queue events, or webhooks).  
* `run_in_thread`           : Execute each ETL job in its own thread to safely isolate heavy transformations.  
* `set_calendar_exclusions` : Skip weekends or data‐blackout periods (e.g., quarterly close days) using custom exclusion calendars.  
* `send_notification`       : Send Slack messages and emails on pipeline failures, retries, or successful completions.  
* `set_concurrency_limits`  : Limit concurrent extract jobs and load jobs to protect source databases.  
* `register_health_check`   : Expose liveness/readiness HTTP endpoints for Kubernetes to ensure scheduling service is healthy.  
* `persist_jobs`            : Back job definitions and runtime state in JSON/YAML or SQLite so pipelines resume after restarts.  
* `set_priority_queue`      : Prioritize real‐time data loads over batch backfills.  
* `get_next_run`            : Query the next scheduled run for any transformation step programmatically.  
* `enable_dynamic_reload`   : Watch YAML config folders and reload job definitions on the fly without restart.  
