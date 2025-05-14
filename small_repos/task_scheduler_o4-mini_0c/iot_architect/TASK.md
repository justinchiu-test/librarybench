# The Task

I am an IoT System Architect managing fleets of smart devices. I want to dispatch firmware updates, collect sensor telemetry, and respond to device heartbeats or alerts. This scheduler integrates with MQTT, HTTP, and custom protocols to coordinate device fleets at scale.

# The Requirements

* `add_event_trigger`       : Fire tasks on MQTT messages, CoAP signals, filesystem events, or webhooks.  
* `run_in_thread`           : Handle each device‐management job in its own thread to avoid blocking other tasks.  
* `set_calendar_exclusions` : Defer updates during regional holidays or maintenance windows.  
* `send_notification`       : Push alerts via SMS, email, Slack, or webhooks when devices report failures.  
* `set_concurrency_limits`  : Throttle concurrent firmware pushes to avoid network congestion.  
* `register_health_check`   : Provide HTTP/sockets probes so container orchestrators know scheduler health state.  
* `persist_jobs`            : Persist job queues and device state in Redis or SQLite across restarts.  
* `set_priority_queue`      : Preempt low‐priority telemetry collection when critical alerts arrive.  
* `get_next_run`            : Query next‐scheduled heartbeat checks or update pushes.  
* `enable_dynamic_reload`   : Dynamically reload device group configs without restarting the scheduler.  
