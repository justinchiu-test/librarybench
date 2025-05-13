# The Task

I am an IoT platform developer at SmartHome Inc. I want to be able to collect temperature, humidity, and motion sensor readings from thousands of devices, convert units, detect malfunctioning nodes, replay data after firmware updates, and provide flexible query APIs for our mobile apps. This code repository offers a robust in-memory time series engine with plugin hooks, replication, and customizable retention to power our IoT backend.

# The Requirements

* `query_cache`           : Cache common device-profile queries (e.g. last 24h temperature for device groups) with TTL for responsive APIs.  
* `write_ahead_log`       : Append each sensor reading to a durable WAL so no user data is lost when services restart.  
* `persistence_snapshot`  : Periodically snapshot the in-memory DB to disk so we can restart quickly after deployments.  
* `anomaly_detector`      : Integrate ML-based detectors to flag unusual temperature or motion patterns per device.  
* `json_import`           : Bulk import historical JSON exports from edge gateways into the central store.  
* `cluster_replication`   : Replicate data across regional clusters for low‐latency reads and high availability.  
* `tag_pattern_query`     : Filter sensors by wildcard or regex tags (e.g. `room:living*`, `type:temp?`) for flexible queries.  
* `retention_policy`      : Auto-expire raw 1-minute readings older than 14 days, aggregate to hourly after that, and delete beyond 90 days.  
* `transformation_hook`   : Apply on-the-fly unit conversions (°F↔°C) or compute dew point as data is ingested.  
* `interpolation_method`  : Use linear or spline interpolation to fill small gaps in sensor readings before visualization.  
