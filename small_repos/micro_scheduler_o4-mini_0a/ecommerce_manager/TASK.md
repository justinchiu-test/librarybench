# The Task

I am an eCommerce Manager orchestrating inventory syncs, pricing updates and promotional campaigns. I want to ensure my jobs run on vendor timezones, handle API rate limits with backoff, let me trigger flash‐sale scripts on demand and keep all store workstreams properly isolated. This code repository will act as a flexible job scheduler for all our automated marketing and inventory tasks.

# The Requirements

* `trigger_job_manually` : Fire off flash‐sale price updates or inventory refetches instantly when we need to react to market changes.
* `configure_persistence` : Use Redis for high availability, or switch to a file-based backend for local testing of campaign workflows.
* `add_job_dependency` : Guarantee that product sync finishes before price optimization begins, and that discount emails only go out after pricing updates.
* `query_jobs` : List all campaigns, next scheduled launch, last success/failure status and tags like `“season=summer”` or `“channel=email”`.
* `schedule_job` : Schedule jobs in vendor timezones such as `Asia/Tokyo` for Japanese markets, automatically adjusting for daylight-saving shifts.
* `apply_backoff_strategy` : Back off on rate-limited vendor API calls with exponential delays and custom caps to avoid blacklisting.
* `set_job_priority` : Prioritize flash‐sale scripts over routine catalog updates so urgent campaigns jump ahead in the queue.
* `register_recurring_job` : Keep daily price checks, weekly stock replenishments and monthly performance reports running indefinitely.
* `persist_jobs` : Store job definitions and run metadata in shelve or JSON so we can resume if the scheduler container restarts mid‐sale.
* `set_tenant_namespace` : Tag jobs per store front (`store_north`, `store_south`) to prevent cross-store interference on a shared pipeline.

