# The Task

I am a Bioinformatics Researcher automating high‐throughput genome analyses. I want to trigger pipelines when new FASTQ data lands, manage concurrency on our compute cluster, and respect lab outages. This scheduler helps me orchestrate thousands of analysis jobs reliably.

# The Requirements

* `add_event_trigger`       : Fire tasks on filesystem changes (new FASTQ) or LIMS webhook notifications.  
* `run_in_thread`           : Execute each alignment or variant‐calling pipeline in its own thread.  
* `set_calendar_exclusions` : Skip runs during lab maintenance days or institutional holidays.  
* `send_notification`       : Notify via email, Slack, or lab pager on job retries or completion.  
* `set_concurrency_limits`  : Limit concurrent jobs per researcher or per cluster node.  
* `register_health_check`   : Expose readiness/liveness probes so our Kubernetes‐based cluster knows the scheduler status.  
* `persist_jobs`            : Back job specs and results in YAML or Redis so analyses resume after node failures.  
* `set_priority_queue`      : Allocate priority to urgent clinical samples over bulk research runs.  
* `get_next_run`            : Programmatically check when the next QC pipeline will start.  
* `enable_dynamic_reload`   : Update pipeline definitions on the fly by editing JSON/YAML configs.  
