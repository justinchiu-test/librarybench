# The Task

I am a Project Manager. I want to oversee the execution of various project tasks and ensure they are completed on time. This code repository helps me track progress and manage task dependencies effectively.

# The Requirements

* `task_inputs_outputs` : Allow project tasks to pass information and results to each other, ensuring smooth workflow.
* `error_handling` : Implement robust error handling to manage unexpected failures in project tasks.
* `alerting` : Notify me of task failures or significant events via email or messaging services to keep the project on track.
* `task_states` : Track the state of each project task, such as pending, running, success, and failure, for better oversight.
* `metadata_storage` : Store metadata for each task execution, including status and execution time, to monitor progress.
* `execution_context` : Maintain a shared context for tasks to exchange data during execution, ensuring consistency.
* `retry_policies` : Configure `max_retries` and `retry_delay_seconds` for tasks to handle intermittent issues.
* `backoff_strategy` : Implement exponential backoff for retry delays to manage resource usage efficiently.
* `task_timeout` : Define maximum execution time for tasks to prevent them from running indefinitely.
* `dynamic_task_creation` : Allow dynamic creation of tasks based on runtime conditions, such as project changes or updates.
