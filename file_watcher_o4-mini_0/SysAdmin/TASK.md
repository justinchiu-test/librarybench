# The Task

I am a system administrator tasked with auditing changes in critical system directories for security and compliance. I want to capture create/modify/delete events, follow or ignore symlinks as needed, and store an immutable history. This repository equips me with a battle-tested, error-resilient watcher I can script or run on a terminal, with CI/CD hooks to notify our alerting system.

# The Requirements

* `cli_interface` : Kick off real-time monitoring from the shell and print audit-grade events.  
* `dry_run_mode` : Test configurations without storing or emitting any audit logs.  
* `event_history_store` : Keep an on-disk, rollover-enabled log of all filesystem events for forensics.  
* `symlink_config` : Fine-tune whether to track symlink targets or treat links as separate entries.  
* `resilient_error_handling` : Retry on NFS or permission-denied errors, with backoff and admin callbacks.  
* `cicd_plugins` : Integrate with our Slack or PagerDuty CI jobs to push alerts on suspicious changes.  
* `handler_registration` : Define handlers per event type (e.g., delete under `/etc/` triggers a lockdown script).  
* `hidden_file_filter` : Exclude system dot-files or only monitor them, depending on policy.  
* `async_io_api` : Use asyncio watchers inside our Python scripts for non-blocking audit tasks.  
* `throttling_control` : Throttle logging under heavy churn to prevent DDoS on our logging backend.  
