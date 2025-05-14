# The Task

I am an Energy Systems Engineer at GreenGrid Analytics. I want to be able to ingest second-level power output and consumption readings from solar inverters and smart meters, apply unit conversions, detect equipment faults, and explore historical trends with downsampling for long-term planning. This code repository gives me a fault-tolerant, high-throughput time series platform with anomaly detection and flexible querying.

# The Requirements

* `query_cache`           : Cache complex aggregation queries (e.g. 15-minute average output per panel) for faster dashboard refresh.  
* `write_ahead_log`       : Persist every incoming power reading to a WAL so that no measurement is lost if a node fails.  
* `persistence_snapshot`  : Snapshot the entire in-memory database at intervals to speed up recovery after maintenance.  
* `anomaly_detector`      : Deploy ML-based detectors to flag sudden drops in power output or meter spikes in real time.  
* `json_import`           : Ingest historical JSON dumps from field data loggers to build a continuous time series archive.  
* `cluster_replication`   : Replicate data across a regional cluster to ensure 24/7 availability for our control center.  
* `tag_pattern_query`     : Filter by site or inverter ID patterns (e.g. `site:alpha*`, `panel:?07`) for targeted diagnostics.  
* `retention_policy`      : Auto-expire raw 1-second data after 7 days, keep minute summaries for 1 year, and roll up to daily beyond that.  
* `transformation_hook`   : Apply on-the-fly unit conversions (e.g. W→kW, compute power factor) as data is ingested.  
* `interpolation_method`  : Fill gaps in sensor data using step or spline interpolation for stable control loop inputs.  
