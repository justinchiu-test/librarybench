# The Task

I am a DevOps engineer responsible for the uptime and reliability of a global microservices platform. I want to be able to schedule, orchestrate, and scale background jobs across multiple regions with failover, observability, and containerized deployment. This code repository gives me a battle-tested scheduler that integrates with Docker and Kubernetes, enforces safe concurrency, provides operational hooks, and offers a real-time dashboard for every task.

# The Requirements

* `DistributedExecution` : Coordinate multiple scheduler instances sharing a task queue across availability zones for high availability and automatic leader election.  
* `PrePostHooks` : Define setup and teardown logic around each job (e.g., inject secrets, rotate keys, clean temporary files).  
* `ConcurrencyLimits` : Enforce per-job and global concurrency caps so no service or database is overwhelmed.  
* `WorkflowChaining` : Chain dependent tasks (build → test → deploy) with conditional branches on success or failure.  
* `MonitoringDashboard` : Access a web UI showing next run times, recent run history, logs, and live status of each scheduler node.  
* `DockerK8sSupport` : Deploy via official Docker image or Helm chart, with customizable values for resource requests, probes, and persistence.  
* `CronExpressionSupport` : Use cron syntax (5- or 6-field) to schedule nightly maintenance, log rotation, and backup jobs.  
* `JitterAndDriftCorrection` : Add configurable random jitter to schedules and auto-correct drift after node restarts to avoid thundering herds.  
* `RecurringTasks` : Automatically requeue recurring jobs like health checks, certificate renewals, and cluster snapshots.  
* `PluginArchitecture` : Write custom plugins for serializers (e.g., Protobuf), transports (e.g., NATS), or your own high-availability leader election strategy.  
