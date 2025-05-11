# The Task

I am a Financial Analyst automating daily report generation, market data fetches, and alert notifications. I want to guarantee that end‐of‐day processes run on schedule, recover from transient API errors, and respect timezones for global exchanges. This code repository delivers a robust scheduler for financial workloads.

# The Requirements

* `graceful_shutdown` : Complete report generation and persist partial data if a shutdown is requested, with a configurable abort threshold.
* `health_check` : Offer a simple HTTP/CLI check so monitoring tools can verify the scheduler before market open.
* `trigger_job` : On‐demand rerun of daily P&L or risk reports without waiting for midnight.
* `schedule_job` : Use cron to schedule jobs at market close in various regions or set custom delays for pre‐market tasks.
* `set_persistence_backend` : Swap persistence to Redis for high throughput or SQLite for local proofs‐of‐concept.
* `timezone_aware` : Schedule EU, US, and APAC tasks in their respective local times, handling DST.
* `exponential_backoff` : Retry data fetches from financial APIs with backoff to handle rate limits and transient outages.
* `define_dependencies` : Chain raw data import → normalization → report assembly → delivery.
* `retry_job` : Configure retry policies on each report step with custom backoff multipliers and max attempts.
* `limit_resources` : Limit concurrent CPU‐heavy analytics jobs to preserve capacity for real‐time alerting.
