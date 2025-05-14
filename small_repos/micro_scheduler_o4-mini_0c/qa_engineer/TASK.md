# The Task

I am a QA Engineer automating regression and performance tests across multiple environments. I want to schedule and chain test suites, handle intermittent failures gracefully, and coordinate resource usage so that tests do not collide. This code repository equips me with a scheduler tailored for testing workflows.

# The Requirements

* `graceful_shutdown` : Let in‐flight tests complete and save partial reports on SIGTERM, with a forced stop timeout.
* `health_check` : Provide a CLI or HTTP endpoint to confirm the scheduler is running before kicking off smoke tests.
* `trigger_job` : Manually launch any test suite instantly after a code push or bug fix.
* `schedule_job` : Define test schedules using delays (for environment spin‐up), intervals, or cron.
* `set_persistence_backend` : Persist test run history in Redis or a lightweight SQLite DB for audit trails.
* `timezone_aware` : Run global test batches in each regional data center’s local time.
* `exponential_backoff` : Retry flaky integration tests with exponential backoff to stabilize CI results.
* `define_dependencies` : Ensure unit tests pass before running integration tests, and integration before performance tests.
* `retry_job` : Retry failed tests up to a configurable count, with delays between attempts.
* `limit_resources` : Cap concurrent browser‐based UI tests to prevent overloading test VMs.
