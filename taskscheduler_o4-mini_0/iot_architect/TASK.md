# The Task

I am an IoT Architect designing workflows for edge devices and central hubs. I want to schedule firmware updates, collect sensor data, and ensure missed transmissions can be replayed when devices reconnect. This code repository gives me a pluggable, resilient scheduler that works in constrained environments and integrates with centralized monitoring systems.

# The Requirements

* `add_storage_backend`         : Pluggable Storage Backends – use SQLite on device or remote Redis for centralized state.
* `set_executor`                : Pluggable Executors – run tasks on lightweight asyncio loops or delegate to threads for heavy processing.
* `on_pre_execute`              : Pre-Execution Hooks – verify device certificates, check connectivity, and gather telemetry before tasks.
* `on_post_execute`             : Post-Execution Hooks – acknowledge data receipts, log success, or trigger retries on failure.
* `add_dependency`              : Task Dependency Graphs – ensure data aggregation runs only after sensor collection tasks succeed.
* `create_api_endpoint`         : RESTful API Endpoints – allow remote commands to trigger firmware updates or query device health.
* `graceful_shutdown`           : Graceful Shutdown & Draining – drain message queues on SIGINT and prevent data loss.
* `send_alert`                  : Alerting & Notifications – push critical alerts via webhook to a central ops dashboard.
* `throttle_task`               : Rate Limiting – throttle sensor polling to conserve battery and bandwidth.
* `register_lifecycle_hook`     : Signal Handling & Lifecycle Hooks – initialize device drivers on startup and close connections on shutdown.
* `catch_up_missed_runs`        : Missed-Run Catch-Up – replay buffered sensor readings after intermittent connectivity.

