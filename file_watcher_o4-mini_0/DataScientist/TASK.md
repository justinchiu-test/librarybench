# The Task

I am a data scientist monitoring a shared directory where raw data files land. I want to quickly prototype ETL scripts that react to new CSVs or JSON dumps, see a live event feed, and replay event history for debugging. This code repository provides a flexible, programmable file-watching core tuned for data pipelines.

# The Requirements

* `cli_interface` : View a live tail of incoming file events in my Jupyter terminal.  
* `dry_run_mode` : Validate my ingest patterns end-to-end without touching production tables.  
* `event_history_store` : Persist a queryable log of file arrivals and modifications for pipeline replay.  
* `symlink_config` : Optionally follow data lake symlinks or skip processed folders.  
* `resilient_error_handling` : Back off and retry on transient network filesystem blips or permission faults.  
* `cicd_plugins` : Trigger Airflow DAGs or other CI/CD jobs when new data lands.  
* `handler_registration` : Map callbacks for ‘new file’ vs ‘file updated’ so I can kickoff different ETL stages.  
* `hidden_file_filter` : Ignore hidden OS files or temp outputs from other processes.  
* `async_io_api` : Leverage asyncio to process multiple file events concurrently in Python.  
* `throttling_control` : Rate-limit event callbacks when hundreds of small files arrive in bulk.  
