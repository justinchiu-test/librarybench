# The Task

I am a data scientist building daily ETL and machine learning pipelines. I want to orchestrate data ingestion, feature engineering, model training, and evaluation in a repeatable, monitored, and resilient way. This code repository provides a lightweight scheduler that handles complex workflows, retries, drift correction, and gives me hooks to load contexts or push metrics to my monitoring stack.

# The Requirements

* `DistributedExecution` : Run schedulers in parallel across dev, staging, and prod clusters, sharing the same task queue for load balancing and failover.  
* `PrePostHooks` : Inject environment variables, activate Python virtualenvs before tasks, and produce cleanup logic to archive intermediate files.  
* `ConcurrencyLimits` : Limit GPU‐bound training jobs to the number of available accelerators and restrict simultaneous ETL tasks to avoid I/O contention.  
* `WorkflowChaining` : Define DAG-like sequences and conditional branches (e.g., if data quality fails, trigger an alert task).  
* `MonitoringDashboard` : Inspect scheduled pipeline runs, view execution logs, track anomalies, and drill down into task latencies.  
* `DockerK8sSupport` : Launch each pipeline stage as a container with proper resource isolation in a Kubernetes cluster.  
* `CronExpressionSupport` : Schedule nightly data pulls and weekly model retraining with cron-style expressions.  
* `JitterAndDriftCorrection` : Prevent synchronized data pulls from all teams by adding jitter, and correct drift after scheduler downtime.  
* `RecurringTasks` : Automatically reschedule feature extraction tasks after each successful data load.  
* `PluginArchitecture` : Extend the scheduler to use custom result serializers (e.g., Pandas to Parquet) or hook into MLflow as a transport.  
