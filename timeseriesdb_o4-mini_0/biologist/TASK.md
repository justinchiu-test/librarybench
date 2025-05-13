# The Task

I am a computational biologist monitoring multi-omics time series experiments. I want to align gene expression, metabolite levels, and phenotype measurements over time, export data for statistical analysis, set alerts on critical biomarkers, and maintain an audit trail for reproducibility. This code repository is my unified TSDB for experimental data.

# The Requirements

* `export_csv(experiment_ids, time_range, include_metadata)` : CSV Export – Produce CSVs of multi-omics series for downstream analysis in R or Python.  
* `define_alert(biomarker_series, condition, threshold, recipients)` : Alerting & Thresholds – Email me or trigger notebooks when a biomarker crosses a critical threshold.  
* `convert_timezone(query, lab_tz)` : Timezone & DST Awareness – Convert all UTC timestamps to local lab time, handling daylight-saving shifts.  
* `join_series(expression_series, phenotype_series, join_mode)` : Multi-Series Joins – Align transcriptomics, proteomics, and phenotypic data by sample time.  
* `stream_updates(sample_series)` : Real-Time Streaming API – Get live feeds as new measurements arrive from instruments.  
* `import_csv(path, mapping)` : CSV Import – Load bulk CSV exports from sequencers and metabolomics instruments.  
* `record_version(entry, user_id, change_reason)` : Versioned Data & Audit Trail – Maintain a full history of data edits for reproducible science.  
* `apply_compression(series_id, method)` : In-Memory Compression – Compress large dense time series to fit in memory during interactive analysis.  
* `cache_query(query_signature, ttl)` : Query Caching – Speed up iterative hypothesis testing by caching expensive joins or aggregations.  
* `limit_cardinality(series_id, tag_key, max_count)` : Cardinality Control – Cap unique sample metadata combinations to guard against runaway factor levels.

