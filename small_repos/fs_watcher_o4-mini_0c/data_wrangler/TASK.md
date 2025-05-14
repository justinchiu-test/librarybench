# The Task

I am a data engineer building a real-time ETL pipeline. I want to process fresh CSV drops, JSON logs, and new parquet files as soon as data lands. This code repository provides a fast, monitored file-watcher that stages, validates, and transforms incoming data before it hits our lakehouse.

# The Requirements

* `start_metrics_endpoint` : push throughput metrics (files/sec, transform durations, backlog size) to Grafana  
* `scan_once`              : manually trigger a full directory crawl for nightly schema drift checks  
* `register_plugin`        : add transformers for CSV → Avro, JSON‐schema validator plugins, and custom event sinks (Kafka, S3)  
* `set_thread_pool_size`   : parallelize file parsing safely so ETL jobs scale across cores  
* `configure_logging`      : use Python `logging` to debug schema errors or data anomalies  
* `set_handler_timeout`    : abort hung parsers or malformed‐data handlers after a threshold  
* `set_throttle_rate`      : avoid overwhelming the Kafka cluster when thousands of files arrive in minutes  
* `generate_change_summary`: summarize daily loads (“120 files ingested, 5 failed validation”) for our SLAs  
* `enable_move_detection`  : detect when datasets are renamed vs. deleted/created to maintain lineage  
* `add_ignore_rule`        : filter out temporary `_SUCCESS` or hidden system files

