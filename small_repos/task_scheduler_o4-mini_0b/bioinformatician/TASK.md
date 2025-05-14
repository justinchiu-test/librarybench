# The Task

I am a Bioinformatician running complex genomics pipelines on HPC and cloud clusters. I want a scheduler that can launch sequence alignment, variant calling, and annotation jobs in the correct order—skip runs during maintenance windows, alert me on any stage failures, track performance metrics, and optionally parallelize I/O-bound steps via asyncio. This code repository will simplify pipeline management.

# The Requirements

* `run_coroutine`             : Enable parallel execution of I/O-intensive data transfers to S3 or NFS via asyncio.  
* `register_error_handler`    : Configure per‐stage handlers to collect logs, send Slack or email alerts, and auto‐retry on transient errors.  
* `schedule_daily`            : Launch daily QC checks and summary reports at specified times.  
* `send_notification`         : Notify me via email or SMS whenever a pipeline step fails, succeeds, or is retried.  
* `start_health_check`        : Provide HTTP probes to verify the scheduler’s readiness in containerized HPC environments.  
* `configure_calendar_exclusions` : Disable analyses on planned cluster maintenance days or national holidays.  
* `add_tag`                   : Label tasks with `“alignment”`, `“variant_call”`, or `“annotation”` for filtering in the dashboard.  
* `define_dependency`         : Construct a DAG so that annotation only starts after variant calling completes successfully.  
* `expose_metrics`            : Push Prometheus metrics such as job duration, queue length, and error counts.  
* `schedule_cron`             : Support cron‐style definitions for monthly reference genome updates or weekly cleanups.  
