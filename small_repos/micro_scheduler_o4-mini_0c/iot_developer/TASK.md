# The Task

I am an IoT Developer orchestrating firmware updates and data syncs across thousands of edge devices. I need to schedule staggered rollouts, handle intermittent connectivity, and ensure safe shutdown if the orchestrator is redeployed. This code repository provides a resilient scheduler suited for distributed IoT workflows.

# The Requirements

* `graceful_shutdown` : Allow in‐progress firmware pushes to finish or checkpoint state before forced stop.
* `health_check` : Expose a lightweight HTTP/CLI endpoint to verify orchestrator readiness before bulk device operations.
* `trigger_job` : Manually initiate a firmware rollout to a specific device group at any time.
* `schedule_job` : Stagger updates with delays, set recurring health‐check pings every few minutes, or use cron for nightly data syncs.
* `set_persistence_backend` : Use Redis for high‐speed state storage or a custom backend tied into our device management DB.
* `timezone_aware` : Schedule updates in device‐local timezones, handling DST for remote sensors.
* `exponential_backoff` : Retry failed firmware pushes or data syncs with exponential backoff to compensate for flaky network links.
* `define_dependencies` : Ensure connectivity check passes before firmware download, and download before install.
* `retry_job` : Configure retries with custom backoff and a maximum attempt ceiling for each device operation.
* `limit_resources` : Throttle concurrent firmware pushes or telemetry uploads to avoid overloading network or gateway hardware.
