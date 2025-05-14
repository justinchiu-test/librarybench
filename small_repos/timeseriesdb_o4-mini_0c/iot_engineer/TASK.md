# The Task

I am an IoT engineer managing a fleet of smart sensors. I want to collect high-frequency telemetry, enforce alarms on abnormal readings, handle data from devices in various time zones, and integrate with third-party analytics platforms. This code repository provides a robust TSDB foundation with streaming, alerting, and import/export capabilities.

# The Requirements

* `export_csv(device_ids, from_ts, to_ts, include_tags)` : CSV Export – Generate CSVs of sensor readings for vendor integration.  
* `define_alert(rule_id, device_series, threshold_type, threshold_value, webhook_url)` : Alerting & Thresholds – Push alerts to edge controllers or cloud functions when sensor data crosses thresholds.  
* `convert_timezone(query, device_local_tz)` : Timezone & DST Awareness – Normalize all device timestamps to UTC and back to device or regional local time with DST rules.  
* `join_series(main_series, aux_series, join_policy)` : Multi-Series Joins – Correlate temperature, humidity, and battery level series on the same timeline.  
* `stream_data(device_series, callback_fn)` : Real-Time Streaming API – Provide an async push interface for incoming telemetry or live query subscriptions.  
* `import_csv(file, mapping_json)` : CSV Import – Onboard historic log dumps from edge gateways.  
* `record_version(series_id, timestamp, payload, user_agent)` : Versioned Data & Audit Trail – Preserve every write with metadata for debugging and compliance.  
* `compress_series_in_memory(series_id, algorithm)` : In-Memory Compression – Use delta-of-delta or RLE to shrink in-RAM storage of high-frequency readings.  
* `cache_query(signature, ttl_ms)` : Query Caching – Cache heavy aggregation queries for dashboard performance.  
* `enforce_cardinality_limit(series_id, max_tags)` : Cardinality Control – Prevent tag cardinality explosion when devices report custom metadata fields.

