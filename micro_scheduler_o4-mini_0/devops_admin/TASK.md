# The Task

I am a DevOps administrator responsible for automated maintenance tasks across a fleet of servers. I want to schedule updates, health checks, and cleanup jobs, monitor their success rates, and ensure high availability through cluster coordination. This repository will give me a lightweight scheduler to maintain reliability and observability.

# The Requirements

* `expose_metrics()` : Publish Prometheus metrics for job durations, success/failure rates, and queue latencies.  
* `schedule_recurring_job()` : Schedule cron-style maintenance jobs (disk cleanup, package updates) to run at regular intervals.  
* `attach_logger()` : Integrate with existing logging infrastructure (syslog, ELK, or cloud logging) for both scheduler and job outputs.  
* `list_jobs()` : Retrieve all scheduled tasks, next run timestamps, last exit codes, run counts, and environment tags like “staging” or “production.”  
* `coordinate_leader_election()` : Ensure only one active scheduler runs maintenance in production via ZooKeeper or Redis‐backed locks.  
* `run_async_job()` : Allow async checks (HTTP health checks) without blocking the scheduler thread.  
* `register_hook()` : Extend on pre-job and post-job events for custom notifications (email, Slack) or integration with on-call systems.  
* `graceful_shutdown()` : Safely terminate ongoing maintenance tasks on SIGTERM, persist schedules, and optionally force-stop after a timeout.  
* `persist_jobs()` : Store job definitions and last run state in a local JSON file or SQLite, so reboots pick up where they left off.  
* `adjust_interval()` : Dynamically scale back or accelerate maintenance frequency via an API when the cluster load changes.  
