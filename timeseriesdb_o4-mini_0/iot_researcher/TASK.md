# The Task

I am an IoT researcher collecting environmental sensor readings. I want to ingest CSV logs from devices, handle sporadic connectivity gaps, auto-compute hourly/daily summaries, query data by device tags, interpolate missing segments (including splines for smooth curves), and both visualize results and archive them as snapshots. This code repository is my lab’s time-series toolkit.

# The Requirements

* `handle_missing_data` : Choose zero-fill, carry-forward, or drop strategies for sensor outages.
* `import_csv` : Bulk-load timestamped sensor logs with tags (device_id, location) and measurements.
* `generate_rollups` : Produce and store hourly/daily rollup summaries alongside raw sensor values.
* `query` : Use a SQL-style DSL to filter by location, device type, or time range and aggregate results.
* `query_by_tags` : Exact matching to pull out a single device’s readings over any time interval.
* `interpolate` : Offer linear, step, or spline interpolation to reconstruct missing data in sensor streams.
* `snapshot` : Take periodic in-memory snapshots for quick recovery in case of lab power failures.
* `compress_memory` : Apply delta/run-length encoding to fit years of data into limited RAM.
* `plot_series` : Plot raw and aggregated sensor data with matplotlib or plotly for quick analysis.
* `export_json` : Serialize selected series or query outputs to JSON for sharing with collaborators.
