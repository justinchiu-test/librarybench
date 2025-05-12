# The Task

I am a DevOps engineer responsible for deploying data pipelines as microservices on Kubernetes. I want a codebase that is easy to configure, monitor, and scale, with built-in metrics, robust error handling, and flexible I/O adapters. This repository offers a standard pipeline framework with CLI tooling, Prometheus integration, and support for batch or streaming modes.

# The Requirements

* `increment_counter` : Emit per-stage processing metrics (success/failure counts) in a thread-safe manner.  
* `skip_on_error` : Ensure malformed records are skipped without crashing the container, with logs for audit.  
* `run_batch` : Schedule and execute jobs via cronjobs with start/end hooks and health checks.  
* `cli_manager` : CLI commands to deploy, upgrade, roll back, and debug pipelines in our cluster.  
* `windowed_operations` : Support time-based windows to aggregate logs or metrics before shipping to staging.  
* `http_adapter` : Configure HTTP sources/sinks with retries, backoff, and custom headers for service hooks.  
* `validate_schema` : Validate incoming payloads against JSON Schema before acceptance to reduce runtime errors.  
* `register_serializer` : Dynamically add support for Protobuf or custom binary formats for downstream systems.  
* `export_prometheus_metrics` : Serve an HTTP `/metrics` endpoint for Prometheus scraping and alerting.  
* `run_streaming` : Deploy long-running streaming jobs on Kubernetes StatefulSets or DaemonSets.  
