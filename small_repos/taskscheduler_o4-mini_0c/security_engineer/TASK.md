# The Task

I am a Security Engineer tasked with vetting and sandboxing all user-submitted scripts before they run in production. I want fine-grained control over job execution, strict auditing, and the ability to pause or revoke tasks at runtime. This repository delivers a job scheduler with introspection APIs, resource caps, structured logs, and persistent state.

# The Requirements

* `list_jobs(filter='untrusted')` : Enumerate all user-submitted tasks.  
* `pause_job(job_id)`             : Quarantine suspicious jobs immediately.  
* `resume_job(job_id)`            : Re-enable vetted jobs after review.  
* `cancel_job(job_id)`            : Kill malicious processes on demand.  
* `remove_job(job_id)`            : Erase decommissioned tasks from the system.  
* `set_concurrency(job_id, 1)`    : Ensure only one instance of an untrusted job runs.  
* `set_global_concurrency(10)`     : Bound total sandboxed containers in production.  
* `set_priority(job_id, 'low')`    : Demote untrusted workloads under peak load.  
* `attach_log_context({'job_id','user','policy'})` : Correlate logs with security policies.  
* `run_in_sandbox(script, {'cpu':1,'mem':'512MB'})` : Launch code in a hardened container.  
* `dump_jobs('/var/lib/jobs.json')` : Store job configs in an encrypted file.  
* `load_jobs('/var/lib/jobs.json')` : Reload tasks with integrity checks on startup.  
* `catch_up_missed_jobs()`        : Replay scans missed during maintenance windows.  
* `inject_task_context({'audit_id','ip_address'})` : Embed audit metadata in the runtime.  
* `serialize_job(args, 'secure_pickle')` : Use safe serializers to prevent code injection.  
* `register_executor('containerd', run_containerd_task)` : Swap in custom container runtimes.  
* `start_api_server(host='0.0.0.0', port=8443)` : Secure REST endpoints with TLS & auth.  
