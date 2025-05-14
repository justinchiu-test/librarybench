# The Task

I am Pat, a FinTech compliance officer. I want to store transaction records immutably, track every update, and generate audit trails on demand. This code repository delivers a JSON DB microservice with strong version control, journaling, and tamper‐evident storage.

# The Requirements

* `restful_api` : HTTP endpoints to log transactions, query by account or date, and manage index rebuilds.
* `versioning` : Immutable history of every transaction document, with rollback disabled except for authorized admins.
* `batch_upsert` : Atomic upload of bulk transaction files at end of day, with full rollback on any validation error.
* `encryption_at_rest` : AES-256 encryption on disk to protect sensitive financial data.
* `update_operation` : Field‐level merges for statuses (e.g., “reconciled”) without altering original transaction amounts.
* `metrics_monitoring` : Prometheus metrics for request throughput, query latency, index hit ratio, and system health.
* `soft_deletes` : Logical deletion of erroneous transactions with a secure purge policy after regulatory window closes.
* `optional_journaling` : Write-ahead log ensures a complete audit trail and supports point-in-time rollback for forensics.
* `atomic_file_persistence` : Safe on-disk writes via temp files + atomic rename so no transaction record is ever partially written.
* `transformation_hooks` : Pre-write hooks to validate anti‐money‐laundering (AML) rules, post-write hooks to notify downstream reporting systems.