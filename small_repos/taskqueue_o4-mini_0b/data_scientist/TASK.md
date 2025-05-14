# The Task

I am a Data Scientist building large-scale ETL and ML pipelines. I want to orchestrate and monitor data preparation, training, and evaluation jobs in a reproducible, auditable fashion. This code repository offers delayed scheduling, traceable runs, and secure backup so I can focus on models instead of infrastructure.

# The Requirements

* `EncryptionAtRest`       : Secure dataset snapshots, logs, and model artifacts on disk.  
* `DelayedTaskScheduling`  : Schedule pre-processing jobs, training starts, or report generations at precise times.  
* `BackupAndRestore`       : Quickly snapshot pipeline state and restore experiments in case of failures or rollbacks.  
* `GracefulShutdown`       : Let long-running training jobs finish cleanly before worker restarts.  
* `DeadLetterQueue`        : Segregate and inspect data-quality failures or script errors for later reprocessing.  
* `MetricsIntegration`     : Expose job durations, success rates, GPU/CPU utilization metrics to Grafana.  
* `UniqueTaskID`           : Tag each experiment or data job with a unique ID for reproducibility.  
* `WebDashboard`           : Visualize pipeline DAGs, per-job status, and historical metrics in real time.  
* `AuditLogging`           : Track every enqueue/dequeue event and parameter sets used in each job.  
* `CLIInterface`           : Enqueue new experiments, list statuses, requeue failed runs, and tail logs from the terminal.  
