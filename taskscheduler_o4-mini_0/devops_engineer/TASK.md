# The Task

I am a DevOps Engineer tasked with maintaining the CI/CD pipelines, infrastructure provisioning, and routine maintenance jobs. I want a scheduler that’s easy to integrate with our deployment tooling, robust under heavy load, and capable of notifying teams immediately on failures. This code repository gives me a modular, RESTful scheduler with full lifecycle control, graceful shutdown, and pluggable modules.

# The Requirements

* `add_storage_backend`         : Pluggable Storage Backends – choose Redis for ephemeral state or PostgreSQL for retention.
* `set_executor`                : Pluggable Executors – toggle between multiprocessing for parallel builds or asyncio for lightweight tasks.
* `on_pre_execute`              : Pre-Execution Hooks – retrieve secrets, check resource availability, and lock deployment artifacts.
* `on_post_execute`             : Post-Execution Hooks – roll back on error, publish metrics to Prometheus, or clean temporary files.
* `add_dependency`              : Task Dependency Graphs – ensure that environment bootstrapping runs before application deployments.
* `create_api_endpoint`         : RESTful API Endpoints – trigger builds, query job logs, or cancel ongoing deployments.
* `graceful_shutdown`           : Graceful Shutdown & Draining – handle SIGTERM for rolling restarts without disrupting in-flight tasks.
* `send_alert`                  : Alerting & Notifications – notify on Slack channels or open Jira tickets when tasks fail.
* `throttle_task`               : Rate Limiting – prevent overloading Kubernetes API by throttling provisioning tasks.
* `register_lifecycle_hook`     : Signal Handling & Lifecycle Hooks – provision resources at startup and drain caches before shutdown.
* `catch_up_missed_runs`        : Missed-Run Catch-Up – replay delayed housekeeping jobs after node reboots or outages.

