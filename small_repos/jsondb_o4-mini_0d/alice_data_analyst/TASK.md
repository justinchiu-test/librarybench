# The Task

I am a marketing data analyst. I want to be able to collect clickstream events in real time, backfill missing events in batches, and drill into historical campaign metrics consistently. This code repository provides a self‐contained JSON database microservice so I can CRUD event documents, query analytics slices, and roll back to earlier data snapshots if I discover tracking errors.

# The Requirements

* `restful_api` : Built‐in HTTP endpoints for inserting new events, querying by campaign or date range, updating metadata, and managing admin tasks.
* `versioning` : Automatic document version tracking so I can inspect modified event payloads and restore prior states if tracking code misfired.
* `batch_upsert` : Atomically upload hundreds or thousands of click events in a single call, guaranteeing all‐or‐none commit/rollback semantics for backfill jobs.
* `encryption_at_rest` : AES‐256 encryption of on-disk JSON files to keep user identifiers and PII secure.
* `update_operation` : Support partial updates on event documents so I can merge new attribution fields without rewriting the full record.
* `metrics_monitoring` : Expose Prometheus‐style counters (request rate, query latency, index hit rate) and a health endpoint so I can monitor ingestion performance.
* `soft_deletes` : Ability to mark erroneous events as deleted without losing them, with the option to undelete or purge per our data retention policies.
* `optional_journaling` : Write-ahead log for safe crash recovery and point-in-time rollback in case a bad schema migration corrupts recent data.
* `atomic_file_persistence` : Use temp files and atomic renames to guarantee no partial writes, even if the process crashes mid-save.
* `transformation_hooks` : Pre‐write callbacks to normalize event timestamps and post‐write hooks to compute derived campaign metrics automatically.