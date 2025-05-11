# The Task

I am a DevOps engineer responsible for configuration management across dozens of microservices. I want to be able to version, expire, stream and restore service‐config documents, hook in monitoring plugins, and swap storage backends as we move from on-prem to cloud object stores. This code repository provides a small, file-based JSON DB with all of those capabilities.

# The Requirements

* `trackVersions` : Automatic document version tracking with history retention and rollback to previous versions  
* `setTTL` : Time-To-Live support to automatically expire stale config documents after a configurable lifespan, via a background sweeper  
* `streamChanges` : Change feed streaming over WebSocket or message queue for real-time monitoring and reactive automation  
* `updateDocument` : Modify existing JSON configs with partial or full‐replacement semantics and field-level merge support  
* `backupRestore` : Snapshots and incremental backups of the DB folder, plus command-line restore tooling  
* `controlConcurrency` : Optimistic or pessimistic locking to coordinate multi-process CI pipelines updating the same configs  
* `encryptAtRest` : AES-256 encryption of stored JSON files to secure sensitive credentials  
* `batchUpsert` : Atomically insert or update multiple config docs in one call, with all-or-none rollback on failure  
* `registerPlugin` : Plugin architecture to add custom validators, alerts, compression filters, or external auth modules  
* `setStorageBackend` : Pluggable storage backends (local FS, in-memory, S3, SQLite, etc.) via a clear backend interface  
