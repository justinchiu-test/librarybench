# The Task

I am a Data Scientist building nightly model retraining pipelines and ad hoc data-cleaning routines. I want to orchestrate jobs that fetch data, train models, and evaluate metrics, with full observability, resource guarantees, and automatic recovery for missed runs. This code repository offers a programmatic scheduler, isolated execution environments, and built-in logging and persistence.

# The Requirements

* `list_jobs()`                   : Programmatically inspect scheduled ETL and training jobs.  
* `pause_job(job_id)`             : Suspend retraining when upstream data is inconsistent.  
* `resume_job(job_id)`            : Resume paused model builds after data validation.  
* `cancel_job(job_id)`            : Abort long-running experiments on demand.  
* `remove_job(job_id)`            : Clean up obsolete pipeline definitions.  
* `set_concurrency(job_id, n)`    : Prevent parallel training jobs from hogging GPUs.  
* `set_global_concurrency(n)`     : Ensure only a fixed number of pipelines run cluster-wide.  
* `set_priority(job_id, p)`       : Promote critical validation runs above routine data syncs.  
* `attach_log_context({'job_id', 'model_name'})` : Tag logs with model metadata for analysis.  
* `run_in_sandbox(script, limits)`: Isolate untrusted notebooks in CPU/RAM-limited containers.  
* `dump_jobs(db_uri)`             : Persist pipeline schedules to our metadata store.  
* `load_jobs(db_uri)`             : Restore schedules after notebook server restarts.  
* `catch_up_missed_jobs()`        : Re-run data ingestion tasks skipped overnight.  
* `inject_task_context({'request_id', 'user'})` : Carry user and experiment IDs into jobs.  
* `serialize_job(params, 'msgpack')`: Use msgpack to handle complex data frames across processes.  
* `register_executor('dask', dask_submit)` : Offload heavy tasks to a Dask cluster.  
* `start_api_server(port=8080)`   : Provide HTTP endpoints for self-service scheduling.  
