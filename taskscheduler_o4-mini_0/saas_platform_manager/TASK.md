# The Task

I am a SaaS Platform Manager offering a “Scheduled Tasks” feature to our customers. I need a multi-tenant scheduler that supports priorities, concurrency limits per account, and RESTful endpoints for self-service. It must persist state across deploys, provide structured logs for billing, and safely run untrusted customer code.

# The Requirements

* `list_jobs(tenant_id)`          : Display all jobs for a given customer.  
* `pause_job(job_id)`             : Allow tenants to pause individual tasks.  
* `resume_job(job_id)`            : Let tenants resume paused workflows.  
* `cancel_job(job_id)`            : Enable on-demand cancellation.  
* `remove_job(job_id)`            : Provide a delete option in our admin UI.  
* `set_concurrency(job_id, limit)`: Enforce per-job concurrency quotas per tenant.  
* `set_global_concurrency(n)`     : Cap total tasks across all tenants for capacity planning.  
* `set_priority(job_id, level)`   : Allow enterprise customers to bump priority.  
* `attach_log_context({'tenant_id','job_id'})` : Tag logs for billing and audit.  
* `run_in_sandbox(code, limits)`   : Safely isolate each tenant’s code in containers.  
* `dump_jobs('s3://bucket/schedules')` : Persist schedules to object storage.  
* `load_jobs('s3://bucket/schedules')` : Hydrate scheduler state on deploy.  
* `catch_up_missed_jobs()`        : Replay tenant jobs missed during upgrades.  
* `inject_task_context({'tenant','user','plan'})` : Carry subscription metadata.  
* `serialize_job(payload, 'json')` : Use JSON to serialize tenant payloads.  
* `register_executor('lambda', aws_lambda_submit)` : Let tenants choose AWS Lambda.  
* `start_api_server(port=9000)`   : Expose multi-tenant RESTful API for job management.  
