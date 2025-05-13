# The Task

I am a DevOps Engineer responsible for infrastructure automation. I want to trigger deployment routines, backups, and rolling upgrades based on code commits, cron patterns, or manual signals while ensuring high availability and strict resource limits. This repository gives me a unified scheduler I can plug into my CI/CD pipelines and container platform.

# The Requirements

* `add_event_trigger`       : Fire tasks on Git webhooks, Docker image updates, or config‐map changes.  
* `run_in_thread`           : Run each deployment or backup procedure in its own thread for isolation.  
* `set_calendar_exclusions` : Skip scheduled maintenance during major holidays or custom blackout windows.  
* `send_notification`       : Notify Slack channels, SMS, or webhooks on success, failure, or retry events.  
* `set_concurrency_limits`  : Enforce global max‐concurrency to avoid overwhelming servers, and per‐job limits for critical tasks.  
* `register_health_check`   : Provide HTTP or socket probes so Kubernetes or Nomad can monitor scheduler health.  
* `persist_jobs`            : Store job definitions and state in Redis or SQLite so maintenance tasks resume after a crash.  
* `set_priority_queue`      : Preempt low‐priority log rotation jobs when higher‐priority rollback tasks arrive.  
* `get_next_run`            : Query when the next security scan or backup will occur.  
* `enable_dynamic_reload`   : Reload playbooks or job specs from Git without tearing down the scheduler.  
