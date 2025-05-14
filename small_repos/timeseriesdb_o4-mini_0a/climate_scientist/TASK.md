# The Task

I am a climate scientist analyzing long-term weather station records. I want to import decades of CSV data, handle sporadic measurement gaps, compute daily and monthly rollups, interpolate missing readings (especially spline for smooth climate trends), run tag-based queries by station or region, visualize temperature/precipitation series, snapshot the database for reproducibility, and export results as JSON for publication. This code repository is my research-grade time-series engine.

# The Requirements

* `handle_missing_data` : Configurable zero-fill, forward-fill, or drop strategies for measurement gaps.
* `import_csv` : Bulk-load historical CSVs, mapping station_id, region tags, timestamps, and climate variables.
* `generate_rollups` : Auto-generate daily, monthly, and annual summaries alongside raw data.
* `query` : SQL-style DSL to select and aggregate by station, region, or climate variable.
* `query_by_tags` : Exact tag matching to retrieve a station’s entire record for analysis.
* `interpolate` : Offer linear, step, or spline interpolation to reconstruct missing climate data smoothly.
* `snapshot` : Periodic serialization of the in-memory DB to disk for reproducibility and continuity.
* `compress_memory` : Delta encoding or run-length encoding to keep decades of data in RAM.
* `plot_series` : Built-in plotting functions to visualize temperature, precipitation, and derived indices.
* `export_json` : Serialize series or queries to JSON arrays or newline-delimited JSON for sharing with journals.
