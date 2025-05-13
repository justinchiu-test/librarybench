# The Task

I am an SRE ensuring our microservices remain reliable under heavy load. I want to enqueue health-check, autoscaling, and backup jobs with full observability, circuit-breaking on external dependencies, and strict quotas to protect our clusters. This code repository offers a secure, multi-tenant task queue with first-class monitoring, audit logging, and retry controls to keep production stable.

# The Requirements

* `MetricsIntegration` : Export detailed Prometheus/Grafana metrics for queue depth, worker latency, retry counts, and error rates.  
* `QuotaManagement` : Impose per-service quotas on concurrent tasks and resource consumption to prevent noisy-neighbor issues.  
* `MultiTenancySupport` : Segregate SRE, backend, and frontend queues, logs, and metrics for clear ownership and access control.  
* `TaskChaining` : Chain service-health checks so dependent checks only run when core infrastructure tests pass.  
* `CircuitBreaker` : Temporarily halt retries against flaky downstream services after repeated 5xx errors to stabilize load.  
* `AuditLogging` : Record every enqueue, retry, cancel, and complete event in an immutable log for post-mortem analysis.  
* `DelayedTaskScheduling` : Schedule routine maintenance and backup jobs at off-peak hours using ETA or delay semantics.  
* `BinaryPayloadSupport` : Attach binary configuration snapshots or VM images as payloads alongside JSON descriptors.  
* `CLIInterface` : Use a command-line tool to quickly list active tasks, adjust quotas, or pause whole queues in emergencies.  
* `EncryptionAtRest` : Keep logs, backups, and state snapshots encrypted to comply with corporate security policies.  
