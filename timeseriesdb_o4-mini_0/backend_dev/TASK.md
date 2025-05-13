# The Task

I am a backend engineer building a scalable metrics service for our microservices platform. I want to be able to ingest, store, and query high-volume time series data reliably while providing flexible export, alerts, and integrations. This code repository gives me a unified toolkit to implement a performant, feature-rich time series database.

# The Requirements

* `export_csv(series_ids, start, end, tags_filter)` : CSV Export – Dump one or multiple series with timestamps, tags, and values for interoperability.  
* `define_alert(rule_id, series_id, threshold, condition, callback)` : Alerting & Thresholds – Trigger callbacks, emails, or webhooks when metrics cross user-defined thresholds.  
* `convert_timezone(query, target_tz)` : Timezone & DST Awareness – Store all data in UTC and translate queries to or from any local time zone with proper daylight-saving support.  
* `join_series(primary_id, other_ids, join_type)` : Multi-Series Joins – Align and merge data from multiple series by timestamp, supporting inner, left, outer, and custom join semantics.  
* `stream_updates(series_id)` : Real-Time Streaming API – Expose an async iterator or callback interface for live ingestion and query result updates.  
* `import_csv(file_path, mapping_config)` : CSV Import – Bulk-load historical data by mapping file columns to timestamp, tags, and values.  
* `record_write(series_id, timestamp, value, tags, user_id)` : Versioned Data & Audit Trail – Maintain historical versions of every write and log operations for compliance and rollback.  
* `apply_compression(series_id, method, block_size)` : In-Memory Compression – Leverage delta encoding, run-length encoding, or other schemes to reduce memory footprint.  
* `cache_query(query_signature, ttl)` : Query Caching – Store results of expensive queries with TTL invalidation to speed up repeat analytics.  
* `limit_cardinality(series_id, tag_key, max_values)` : Cardinality Control – Track and cap the number of unique tag combinations per series to prevent tag explosion.

