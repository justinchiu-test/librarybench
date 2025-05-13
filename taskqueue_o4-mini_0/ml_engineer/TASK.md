# The Task

I am an ML engineer designing a model training and evaluation platform. I want to enqueue data-preprocessing, training, and validation tasks; schedule hyperparameter sweeps; and enforce per-team GPU quotas. This code repository delivers a flexible, secure, and observable task orchestration layer—complete with chaining, delayed runs, and binary payload support for model artifacts.

# The Requirements

* `MetricsIntegration` : Collect Prometheus/Grafana metrics on training batch durations, resource utilization, retry counts, and failure rates.  
* `QuotaManagement` : Allocate per-team quotas on GPUs, CPUs, and memory to ensure fair resource sharing.  
* `MultiTenancySupport` : Provide isolated queues, artifact storage, and metrics per ML project or research group.  
* `TaskChaining` : Define workflows so data cleaning runs before feature extraction, which runs before model training and evaluation.  
* `CircuitBreaker` : Pause retries to data stores or external APIs if a sudden spike of failures is detected during preprocessing.  
* `AuditLogging` : Keep an immutable log of every experiment run, including hyperparameters, retries, and results for reproducibility.  
* `DelayedTaskScheduling` : Queue training jobs to start when GPUs free up or at scheduled off-peak times.  
* `BinaryPayloadSupport` : Persist large model checkpoints, embeddings, and serialized pipelines alongside JSON experiment metadata.  
* `CLIInterface` : Expose CLI tools to launch experiments, check queue status, cancel runs, and stream real-time logs.  
* `EncryptionAtRest` : Encrypt datasets, checkpoints, and logs on disk to protect proprietary research and customer data.  
