# The Task

I am a Backend Developer building a user-facing service that processes large‐scale image transformations. I want a robust background dispatcher that I can integrate via REST, tune for high throughput, and observe in production.

# The Requirements

* `api_enqueue_image_task` : HTTP/REST API endpoints to submit new image jobs, query progress, cancel or bump priority.  
* `set_queue_limits` : Define per-queue or global concurrency limits to throttle CPU/GPU usage under load.  
* `register_pluggable_backend` : Seamlessly switch between a local thread pool, process pool, or an asyncio‐based runner for different environments.  
* `emit_service_metrics` : Export metrics (jobs/sec, avg latency, retries, errors) in Prometheus format for Grafana alerts.  
* `hot_reload` : Dynamically update retry counts, timeout values, and logging levels without rebooting the service.  
* `plugin_system` : Enable plugins for custom serializers (JPEG, PNG, WebP), metrics sinks (StatsD, OpenTelemetry), and pre/post hooks.  
* `rbac_control` : Enforce role-based permissions so only authorized microservices or users can submit or cancel jobs.  
* `dag_visualization` : Generate dependency graphs for multi‐stage image pipelines (decode → transform → upload) to simplify debugging.  
* `dead_letter_queue` : Automatically divert irrecoverable image processing tasks into a dead letter queue for manual reprocessing.  
* `cron_scheduler` : Support both one-off and recurring image cleanup or batch‐generate jobs via cron expressions.

---

