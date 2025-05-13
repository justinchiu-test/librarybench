# The Task

I am a Data Scientist. I want to build a reproducible data pipeline that ingests, transforms, and trains models on schedule or when new data arrives. This code repository will help me orchestrate experiments, track outcomes, and adjust schedules without manual intervention.

# The Requirements

* `trackJobStats()` : Record how many pipeline runs succeeded or failed, average data processing time, and last run details.  
* `setTimezone()` : Schedule data pulls from global sources in their local timezones, automatically adapting for DST changes.  
* `onEventTrigger()` : Kick off ETL or retraining when new CSV files land in a watcher directory or a Kafka/Redis stream signal is received.  
* `addTagMetadata()` : Tag jobs by dataset, model type, or experiment name for easy filtering and reporting.  
* `getNextRunTime()` : Query when the next retraining or validation job is due, so I can align with team sync-ups.  
* `shutdownGracefully()` : Gracefully halt all jobs before a critical notebook update or cluster maintenance.  
* `pauseTasks()` : Pause heavy GPU training tasks while I tweak hyperparameters, then resume them later.  
* `enableOverlapLocking()` : Ensure no two training jobs for the same model version run concurrently to avoid resource conflicts.  
* `persistentStorage()` : Persist pipeline definitions in YAML and job state in SQLite across Jupyter server restarts.  
* `retryStrategy()` : Automatically retry flaky data downloads or model checkpoint saves with exponential backoff and random jitter.  
