# The Task

I am an IoT Coordinator managing fleets of sensors across global sites. I want to schedule data collection, firmware checks and alerts in each site’s local timezone, retry on flaky connections with backoff, and manually trigger diagnostics for troubleshooting. This code repository will be my scheduler to orchestrate device workflows reliably, with stateful recovery and tenant‐style isolation for each device group.

# The Requirements

* `trigger_job_manually` : Perform on-demand firmware health checks or manual sensor diagnostics during maintenance windows.
* `configure_persistence` : Switch between lightweight file persistence in edge gateways and Redis clusters in the cloud.
* `add_job_dependency` : Run sensor calibration before data collection, and run aggregation only after collections complete.
* `query_jobs` : Inspect all sensor group jobs, next data pull windows, last run statuses and tags like `“region=eu-west-1”`.
* `schedule_job` : Schedule recurring data pulls in local site timezones (e.g. `Australia/Sydney`) with correct DST handling.
* `apply_backoff_strategy` : Apply exponential backoff on connectivity failures to unreliable edge devices.
* `set_job_priority` : Mark critical alert tasks (e.g. smoke detectors) as high priority so they preempt routine telemetry pulls.
* `register_recurring_job` : Automate continuous telemetry captures, weekly firmware updates and daily status summaries.
* `persist_jobs` : Persist the entire job graph and run history to disk (pickle or JSON) so edge devices can recover after power cycles.
* `set_tenant_namespace` : Namespace jobs per device fleet (`fleet_north`, `fleet_south`) to avoid cross-fleet scheduling conflicts.
