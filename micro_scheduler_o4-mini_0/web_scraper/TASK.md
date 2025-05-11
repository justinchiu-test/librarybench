# The Task

I am a backend engineer building a distributed web crawler. I want to schedule page fetch jobs, track performance, distribute load across nodes, and dynamically throttle or boost crawl rates. This micro-scheduler will coordinate scraping tasks at scale.

# The Requirements

* `expose_metrics()` : Expose histograms of page fetch latency, counters of success/failure, and gauges for queue depth.  
* `schedule_recurring_job()` : Register recurring crawl jobs (e.g., every 10 minutes for high-priority domains).  
* `attach_logger()` : Plug into structured logging frameworks (JSON logs to stdout) for crawler traces.  
* `list_jobs()` : Query active crawl jobs, next scheduled crawl, last HTTP status code, run count, and tags like “news_sites.”  
* `coordinate_leader_election()` : Run multiple scraper instances with Redis locks or etcd to assign domains exclusively to one node.  
* `run_async_job()` : Use asyncio‐based HTTP clients to fetch hundreds of pages concurrently without blocking.  
* `register_hook()` : Add hooks for custom rate-limit backoff strategies, proxy rotation, or dynamic prioritization.  
* `graceful_shutdown()` : On deployment or SIGTERM, finish in‐flight fetches, persist queue state, then shut down within a forced timeout.  
* `persist_jobs()` : Serialize the crawl queue and per-job state to disk (pickle or JSON) for restart continuity.  
* `adjust_interval()` : Dynamically throttle or increase crawl interval for specific domains via API to respect robots.txt or server load.  
