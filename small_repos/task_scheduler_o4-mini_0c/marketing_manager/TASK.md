# The Task

I am a Marketing Automation Manager running multi‐channel campaigns. I want to send emails, SMS, or push notifications triggered by user sign‐ups or segment events, while respecting business hours and holiday rules. This code repository lets me design, schedule, and monitor all campaign workflows in one place.

# The Requirements

* `add_event_trigger`       : Fire tasks on CRM webhooks, form submissions, or message queue events.  
* `run_in_thread`           : Execute each campaign step (email send, data enrichment) in isolated threads.  
* `set_calendar_exclusions` : Avoid sending blasts on weekends, public holidays, or company blackout days.  
* `send_notification`       : Alert me via Slack or email if a campaign step fails or retries.  
* `set_concurrency_limits`  : Control concurrent sends per campaign to avoid throttling by ESPs.  
* `register_health_check`   : Expose a readiness probe so our container platform alerts if the scheduler is down.  
* `persist_jobs`            : Persist campaign definitions and run history to JSON or Redis across restarts.  
* `set_priority_queue`      : Prioritize transactional notifications over promotional campaigns.  
* `get_next_run`            : Look up when each follow‐up email or SMS will fire.  
* `enable_dynamic_reload`   : Update campaign schedules on the fly by editing a shared endpoint or config file.  
