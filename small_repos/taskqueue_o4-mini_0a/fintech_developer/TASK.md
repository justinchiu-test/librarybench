# The Task

I am a fintech developer building a payments settlement system. I want to enqueue transaction tasks, enforce per-client quotas, chain fraud-check tasks before settlement, and keep an immutable audit log for regulatory compliance. This code repository supplies a secure, audited, and metrics-rich task queue tailored for financial workloads.

# The Requirements

* `MetricsIntegration` : Provide Prometheus/Grafana metrics for throughput, latency, retry rates, and failure rates per payment type.  
* `QuotaManagement` : Enforce per-merchant and per-customer quotas on transaction volumes and CPU usage.  
* `MultiTenancySupport` : Isolate settlement queues, audit logs, and metrics for each financial partner with strict ACLs.  
* `TaskChaining` : Sequence fraud-detection, risk-scoring, and ledger-update tasks so payments only settle after all checks pass.  
* `CircuitBreaker` : Stop retrying calls to the external anti-fraud API after a configurable error threshold to avoid lock-ups.  
* `AuditLogging` : Maintain an immutable, tamper-evident trail of every payment enqueue, retry, authorization, and cancellation.  
* `DelayedTaskScheduling` : Schedule high-value batch settlements at specific clearing cycle times or after a hold period.  
* `BinaryPayloadSupport` : Store encrypted binary blobs (e.g., signed transaction payloads) alongside JSON metadata.  
* `CLIInterface` : Offer CLI commands for running test transactions, querying queue health, and replaying failed jobs.  
* `EncryptionAtRest` : Encrypt all persisted logs, payload snapshots, and database snapshots to comply with PCI-DSS.  
