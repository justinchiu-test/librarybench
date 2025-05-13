# The Task

I am a Game Server Administrator coordinating world events and maintenance across global servers. I want to trigger tournaments at scheduled times, perform rolling restarts, and react to player‐driven webhooks, all while keeping an eye on uptime and player alerts. This scheduler ties into my monitoring and chat ops for seamless operations.

# The Requirements

* `add_event_trigger`       : Fire tasks on in‐game webhook events, filesystem updates or message queue signals.  
* `run_in_thread`           : Run each maintenance or tournament‐start job in its own thread to avoid blocking.  
* `set_calendar_exclusions` : Avoid scheduling events on holidays when server population is low.  
* `send_notification`       : Post to Discord/Slack, send SMS, or trigger webhooks on failures or countdown warnings.  
* `set_concurrency_limits`  : Limit concurrent restart jobs to avoid knocking out too many servers at once.  
* `register_health_check`   : Expose liveness and readiness probes so Kubernetes/Swarm can monitor the scheduler.  
* `persist_jobs`            : Store event schedules and state in JSON or Redis so restarts don’t clear the queue.  
* `set_priority_queue`      : Ensure hotfix deployments interrupt lower‐priority world‐event tasks.  
* `get_next_run`            : Programmatically query when the next tournament kickoff or maintenance window begins.  
* `enable_dynamic_reload`   : Reload event scripts and configs on the fly without downtime.  
