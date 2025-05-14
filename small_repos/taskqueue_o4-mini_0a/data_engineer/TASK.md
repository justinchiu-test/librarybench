# The Task

I am a data engineer responsible for orchestrating ETL pipelines that pull, transform, and load data from multiple sources. I want to be able to schedule and chain hundreds of data-processing jobs, enforce resource budgets per pipeline, and have full visibility into performance and failures. This code repository gives me a resilient, metrics-driven task queue with quota controls, delayed scheduling, and an immutable audit trail—perfect for production data workflows.

# The Requirements

* `MetricsIntegration` : Emit Prometheus/Grafana-compatible metrics on throughput, latencies, retries and failure rates across all ETL jobs.  
* `QuotaManagement` : Enforce per-pipeline CPU and memory quotas so no single data flow starves shared cluster resources.  
* `MultiTenancySupport` : Isolate pipeline queues, file storage, and metrics per team or project to avoid cross-team interference.  
* `TaskChaining` : Declare dependencies so transformations only start after upstream extracts and cleans complete successfully.  
* `CircuitBreaker` : Pause retries for connectors hitting persistent downstream API failures to prevent cascading load spikes.  
* `AuditLogging` : Maintain an immutable audit trail of each job’s enqueue, start, retry, success, and failure events for compliance.  
* `DelayedTaskScheduling` : Allow ETL jobs to be enqueued with specific ETAs so daily and hourly reports run at precise times.  
* `BinaryPayloadSupport` : Store pickled Python objects or Parquet file references alongside JSON metadata in the file store.  
* `CLIInterface` : Provide command-line tools for launching ad-hoc jobs, inspecting queue depth, canceling stuck tasks, and tailing logs.  
* `EncryptionAtRest` : Encrypt persisted intermediate files, logs, and snapshots so sensitive PII remains secure on disk.  
