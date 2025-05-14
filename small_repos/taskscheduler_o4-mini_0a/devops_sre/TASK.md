# The Task

I am an SRE responsible for scheduling maintenance, scaling, and backup tasks across our cloud infrastructure. I want a reliable, observable scheduler that can run day-to-day operational jobs, integrate with our monitoring stack, and enforce service-level resource boundaries. This code repository provides a battle-tested framework that plugs into our observability, locking, and containerization tools.

# The Requirements

* `export_metrics` : Real-time Prometheus/StatsD metrics on job success/failure counts, queue lengths, and execution latencies for each maintenance task.  
* `configure_executor` : Swap between threaded, multiprocessing, or asyncio executors based on task type (shell commands vs. API calls) without touching the task code.  
* `acquire_distributed_lock` : Use ZooKeeper or Redis locks so that only one executor runs the daily backup or cleanup job in our multi-region cluster.  
* `dashboard_ui` : Simple web dashboard to visualize upcoming jobs, track historical runs, and manage retry queues for failed tasks.  
* `attach_log_context` : Structured logging with per-job context (job_id, target_host, schedule_type) forwarded into our ELK stack.  
* `start_api_server` : Expose RESTful endpoints for on-the-fly task triggers, health checks, and dynamic schedule adjustments.  
* `run_in_sandbox` : Optionally run untrusted or third-party scripts in isolated subprocesses or lightweight containers with CPU/memory caps.  
* `set_job_priority` : Prioritize critical security patches and high-urgency maintenance tasks over routine housekeeping when nodes are under heavy load.  
* `register_lifecycle_hook` : Startup hooks to reload infrastructure state, pre-shutdown hooks to pause new tasks, post-shutdown to alert on incomplete jobs.  
* `serialize_job` : Custom serializers (JSON, msgpack) and pickling support to dispatch complex host inventories and playbook arguments.  
