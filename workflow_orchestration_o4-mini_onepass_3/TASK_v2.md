# The Task Update

We want some updated functionality. For version 2, 

# New features to add:

Time-based scheduling. 

I want to run workflows on a schedule, like every hour or once a day. Please add some time-based scheduling. You can simulate time via `datetime` or something.

Retry policies. 

Some steps fail intermittently, so I want to retry them a few times before giving up.
Allow each task to have a `max_retries` and `retry_delay_seconds`, then update the task execution engine to retry failed tasks with backoff.

Task inputs/outputs.

Tasks should be able to pass data to each other. Allow tasks to consume outputs from other tasks via return values or context, probably via an execution context (dictionary) passed between tasks.

Logging

I want to track when each task ran, how long it took, and any logs it wrote."

Store metadata per task execution:
* start time, end time
* exit status (success/failure)
* log output (optional)