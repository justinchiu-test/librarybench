# The Task

I am a DevOps engineer monitoring our fleet of servers. I want to record CPU, memory, and network metrics, handle missing telemetry, roll up metrics hourly and daily, run ad-hoc tag-based queries (e.g. by host or datacenter), visualize trends to detect anomalies, and snapshot the in-memory store for fast restart. This code repository is my lightweight time-series database.

# The Requirements

* `handle_missing_data` : Zero-fill, carry-forward or drop missing metric points.
* `import_csv` : Import CSV dumps from monitoring agents, mapping timeseries columns to timestamp, tags (host, region), and values.
* `generate_rollups` : Auto-generate hourly and daily rollups for CPU, RAM and network I/O.
* `query` : SQL-like DSL to select metrics, filter by host or service, and group by time intervals.
* `query_by_tags` : Retrieve a specific server’s time window with exact tag matching (host=“web-01”).
* `interpolate` : Step or linear interpolation to smooth out telemetry gaps.
* `snapshot` : Periodically write an in-memory snapshot to disk for sub-second recovery after crashes.
* `compress_memory` : Apply delta encoding or run-length encoding to minimize RAM usage under heavy load.
* `plot_series` : Visualize real-time or historical metrics using built-in matplotlib/plotly functions.
* `export_json` : Export failure or load patterns as JSON arrays/newline-delimited JSON for alerting pipelines.
