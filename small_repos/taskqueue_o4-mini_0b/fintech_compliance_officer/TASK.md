# The Task

I am a FinTech compliance officer overseeing transaction processing workflows. I want an immutable, secure, and monitored task queue so that every payment job, refund, or settlement step is traceable, auditable, and recoverable under strict regulatory mandates. This code repository ensures data protection, auditability, and operational resilience.

# The Requirements

* `EncryptionAtRest`       : Protect transaction payloads, personally identifiable information, and logs while at rest.  
* `DelayedTaskScheduling`  : Enforce settlement holds and time-based release of funds automatically.  
* `BackupAndRestore`       : Snap and restore queue state for regulatory drills and disaster-recovery testing.  
* `GracefulShutdown`       : Drain and complete in-flight settlement tasks during maintenance windows.  
* `DeadLetterQueue`        : Isolate transactions that breach limits or exceed retry thresholds for manual review.  
* `MetricsIntegration`     : Publish throughput, failure rates, retry counts, and latency histograms to Grafana.  
* `UniqueTaskID`           : Guarantee each financial transaction carries a non-collision, traceable ID.  
* `WebDashboard`           : Provide auditors with a live UI to drill down into any job, view payload details, and replay as needed.  
* `AuditLogging`           : Keep an immutable ledger of enqueue, update, retry, and cancellation events for compliance audits.  
* `CLIInterface`           : Allow on-call engineers to enqueue ad hoc tasks, cancel suspect jobs, and extract log slices via command line.  
