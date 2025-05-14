# The Task

I am a quantitative trader analyzing tick-level market data across multiple instruments. I want sub-second ingestion, live event alerts on price movements, timezone-aware timestamping, and the ability to join order flow with trade prints. This code repository is my low-latency time series engine with full observability and operational controls.

# The Requirements

* `export_csv(quotes_ids, start_time, end_time, field_selection)` : CSV Export – Dump time series of bids, asks, and trades for research.  
* `define_alert(alert_id, series_id, operator, price_threshold, notification_target)` : Alerting & Thresholds – Fire webhooks or messages to our trading algos when thresholds hit.  
* `convert_timezone(trading_query, exchange_tz)` : Timezone & DST Awareness – Normalize all exchange timestamps to UTC and present results in any local exchange time with DST.  
* `join_series(base_series, overlay_series, join_type, tolerance)` : Multi-Series Joins – Align order book updates with executed trade series.  
* `stream_updates(series_identifier)` : Real-Time Streaming API – Subscribe to sub-millisecond tick streams or query result diffs.  
* `import_csv(historical_file, column_map)` : CSV Import – Ingest months of historical tick data in bulk.  
* `record_audit(series_id, operation, user, timestamp)` : Versioned Data & Audit Trail – Keep a full trail of data writes and parameter changes for compliance.  
* `apply_compression(series_id, compression_type)` : In-Memory Compression – Compress high-frequency ticks to save memory without losing precision.  
* `cache_query(query_id, valid_for_sec)` : Query Caching – Cache heavy factor-model computations for rapid replay.  
* `limit_cardinality(series_id, tag_key, max_unique)` : Cardinality Control – Prevent runaway dimension explosion in exotic instrument tags.

