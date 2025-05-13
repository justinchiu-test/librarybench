# The Task

I am a data engineer building nightly ETL pipelines for our financial data warehouse. I want to be able to reliably schedule, monitor, and scale dozens of extract-transform-load jobs that pull from third-party APIs, clean, aggregate, and write to our data lake. This code repository helps me orchestrate these tasks across multiple servers, track their performance, and enforce resource limits so that heavy jobs don’t starve the system.

# The Requirements

* `export_metrics` : Built-in Prometheus and StatsD exporters to record job counts, success/failure rates, and execution latencies for each ETL pipeline.  
* `configure_executor` : Pluggable executors so I can switch between threading, multiprocessing, or asyncio workers without rewriting pipeline code.  
* `acquire_distributed_lock` : Redis and ZooKeeper locks to ensure only one instance of the nightly job runs at a time in our HA scheduler cluster.  
* `dashboard_ui` : A lightweight web dashboard to view job schedules, success/failure trends, retry queues, and historical run details.  
* `attach_log_context` : Structured logging integration that tags every log line with job_id, data_source, and schedule metadata for downstream log analysis.  
* `start_api_server` : RESTful endpoints to trigger ad hoc data loads, query current job status, and cancel or reprioritize tasks via HTTP.  
* `run_in_sandbox` : Ability to run each pipeline in a sandboxed subprocess or container with configurable CPU and memory limits to protect critical workloads.  
* `set_job_priority` : Job prioritization so high-value data loads (e.g. risk calculations) preempt lower-priority tasks when resources are constrained.  
* `register_lifecycle_hook` : Signal handling and lifecycle hooks for startup initialization (DB connection warm-up), pre-shutdown checkpoints, and post-shutdown cleanup.  
* `serialize_job` : Job serialization with pickling or custom JSON/msgpack serializers so complex ETL parameters travel across processes and hosts seamlessly.  
