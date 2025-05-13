# The Task

I am a Site Reliability Engineer at CloudOps Co. I want to be able to collect high-frequency system metrics (CPU, memory, network) from hundreds of servers, detect anomalies in real-time, replay lost data on restart, and provide fast ad-hoc querying for on-call rotations. This code repository provides a rock-solid in-memory time series backend with WAL, snapshots, clustering and custom hooks so our monitoring stack never misses a beat.

# The Requirements

* `query_cache`           : Cache heavy aggregation queries (e.g. 5-minute p95 CPU) with TTL invalidation to speed up alert dashboards.  
* `write_ahead_log`       : Append all writes from Prometheus-style scrapers to a durable WAL, ensuring no metric is lost during crashes or upgrades.  
* `persistence_snapshot`  : Periodically dump in-memory metrics to disk so nodes can restart and catch up in seconds, not minutes.  
* `anomaly_detector`      : Hook in ML-based detectors to automatically flag unusual traffic spikes or CPU usage anomalies for PagerDuty alerts.  
* `json_import`           : Bulk import historical metric dumps in JSON when migrating from legacy systems or testing new alert rules.  
* `cluster_replication`   : Keep metrics in sync across a distributed cluster for high availability and load-balanced query serving.  
* `tag_pattern_query`     : Query hosts by wildcard or regex (e.g. `env:prod*`, `region:us-?ast`) to troubleshoot groups of servers.  
* `retention_policy`      : Auto-expire detailed metrics older than 30 days, downsample to hourly for 30–90 days, and remove beyond 90 days.  
* `transformation_hook`   : Run custom scripts on ingest (e.g. normalize units, derive request-per-second from counters).  
* `interpolation_method`  : Use linear or step interpolation to fill in brief scrape gaps so SLIs remain continuous.  
