# The Task

I am a Quantitative Trader automating market data ingestion and risk calculations. I want to schedule tasks around market hours, skip holidays, and ensure overnight jobs complete before market open. This repository gives me precise timing, robust retries, and full audit trails for compliance.

# The Requirements

* `add_event_trigger`       : Fire tasks on live data‐feed messages or on‐demand API webhooks.  
* `run_in_thread`           : Run heavy Monte Carlo simulations or optimizers in isolated threads.  
* `set_calendar_exclusions` : Exclude exchange holidays, weekends, or custom trading‐session outages.  
* `send_notification`       : Send SMS and secure email alerts on job failures or threshold breaches.  
* `set_concurrency_limits`  : Cap concurrent data‐feeds or risk‐calc jobs to safeguard compute budgets.  
* `register_health_check`   : Use HTTP health endpoints so orchestration tools know when the scheduler is healthy.  
* `persist_jobs`            : Store job metadata and state in SQLite or Redis for audit and recovery.  
* `set_priority_queue`      : Preempt low‐priority analytics when high‐priority trading‐hour tasks arrive.  
* `get_next_run`            : Query next run times to synchronize with market‐open events.  
* `enable_dynamic_reload`   : Dynamically adjust strategies by reloading config files without downtime.  
