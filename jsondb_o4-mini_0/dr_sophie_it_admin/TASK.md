# The Task

I am Dr. Sophie, a hospital IT administrator. I want to ensure patient record updates are secure, versioned, and auditable while allowing clinicians to correct mistakes without data loss. This repository acts as a lightweight JSON document store microservice with enterprise‐grade security and compliance features.

# The Requirements

* `restful_api` : Secure HTTP endpoints (TLS, token auth) for CRUD on patient summaries, lab results, and administrative tasks.
* `versioning` : Full history retention of each patient record, with the ability to roll back to prior versions to audit treatment changes.
* `batch_upsert` : Atomically ingest daily lab batches or bulk patient updates, ensuring either all data lands or none does.
* `encryption_at_rest` : AES-256 encryption on disk to satisfy HIPAA requirements for protected health information.
* `update_operation` : Fine-grained merges so clinicians can add new observations without overwriting existing notes.
* `metrics_monitoring` : Health checks and performance counters for API latency, I/O throughput, and index hit rate, integrated with Prometheus.
* `soft_deletes` : Logical deletes for decommissioned or transferred patient files, with policies for automatic purge after retention windows.
* `optional_journaling` : Write-ahead log for guaranteed crash recovery and forensic point-in-time rollback in case of system failure.
* `atomic_file_persistence` : Safe on-disk writes using temp files and atomic renames to avoid partial or corrupted records.
* `transformation_hooks` : Pre-write hooks to validate PHI schemas, anonymize fields for research, and post-write hooks for triggering audit logs.