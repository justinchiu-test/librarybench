# The Task

I am an IoT network operator managing thousands of edge devices that report telemetry and execute remote firmware updates. I want a scheduler that reliably pushes jobs to device gateways, tracks success, and can isolate untrusted code from core services. This repository gives me flexible executors, distributed coordination, and full observability across our global network.

# The Requirements

* `export_metrics` : Prometheus and StatsD exporters to capture push job counts, update success/failure rates, and latency for each device group.  
* `configure_executor` : Easily change between multithreading, multiprocessing, or asyncio to optimize gateway throughput without rewriting device logic.  
* `acquire_distributed_lock` : Redis-based distributed locks to guarantee only one gateway cluster runs a firmware rollout at any time.  
* `dashboard_ui` : Web interface to visualize scheduled updates, live deployment status per region, and manage retry queues for offline devices.  
* `attach_log_context` : Structured logs tagged with job_id, device_group, firmware_version, and schedule metadata for audit and debugging.  
* `start_api_server` : REST endpoints for on-demand OTA pushes, status queries, and canceling or re-prioritizing jobs remotely.  
* `run_in_sandbox` : Sandbox each device script or firmware validation job in containers/subprocesses with strict CPU and memory limits.  
* `set_job_priority` : Prioritize emergency security patches over routine telemetry collection tasks under constrained gateway resources.  
* `register_lifecycle_hook` : Hooks at startup (load device certificates), pre-shutdown (drain active connections), and post-shutdown (archive logs).  
* `serialize_job` : Use pickling or msgpack to serialize complex firmware blobs, device credentials, and update parameters across processes.  
