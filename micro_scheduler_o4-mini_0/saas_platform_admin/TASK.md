# The Task

I am a SaaS Platform Administrator managing background tasks for multiple customer tenants. I want to schedule billing runs, usage reports, data archival and health monitors on a per‐tenant basis, with isolation, retry policies and emergency manual triggers. This code repository will be my multi‐tenant micro scheduler to keep each customer’s jobs siloed yet managed by a single service.

# The Requirements

* `trigger_job_manually` : Manually run a tenant’s billing cycle or emergency data export without affecting others.
* `configure_persistence` : Swap persistence layers between SQLite for dev and Redis for production, all via a common interface.
* `add_job_dependency` : Ensure usage aggregation completes before invoice generation for each tenant.
* `query_jobs` : Provide an API to list all tenant jobs, upcoming runs, last statuses and tags like `“tier=enterprise”`.
* `schedule_job` : Schedule jobs in each tenant’s preferred timezone (e.g. `America/New_York` vs `Asia/Kolkata`), handling DST boundary changes.
* `apply_backoff_strategy` : Use exponential or custom backoff for transient failures on tenant‐specific tasks (e.g. report exports).
* `set_job_priority` : Elevate high‐value customer tasks (e.g. SLA recovery runs) above standard maintenance jobs.
* `register_recurring_job` : Support per-tenant recurring tasks: daily usage summaries, monthly invoices, quarterly audits.
* `persist_jobs` : Persist each tenant’s job definitions and run history to disk in JSON so recovery is tenant-aware.
* `set_tenant_namespace` : Enforce complete namespace isolation so `tenant_alpha` jobs never collide with `tenant_beta`.

