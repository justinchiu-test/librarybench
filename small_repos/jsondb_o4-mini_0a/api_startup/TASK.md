# The Task

I am a startup founder racing to spin up a real-time analytics microservice. I want to be able to push, query, and purge events at scale with minimal ops overhead. This code repository will serve as our lightweight JSON-based DB engine that we expose over HTTP so our front-end and back-end teams can iterate at lightning speed.

# The Requirements

* `setTTL` : Automatic expiry of documents after a configurable lifespan, with background sweeper to clear stale event logs.
* `createIndex` : Single-field and compound indexes that load on startup and automatically update on writes for instant lookups on userID and eventType.
* `encryptAtRest` : AES-256 encryption of all JSON files on disk to safeguard PII in our logs.
* `enforceSchema` : JSON Schema enforcement to ensure every event has timestamp, userID, and eventType fields.
* `registerPlugin` : Plugin architecture to slot in custom auth, real-time compression, or replication to our cloud buckets.
* `batchUpsert` : Atomically ingest hundreds of events in one call, with commit/rollback semantics on failure.
* `persistAtomically` : Safe on-disk storage using temp files and atomic renames to avoid corruption under heavy writes.
* `delete` : Remove old events by ID or by query filters, with option for soft-delete so we can review before purge.
* `softDelete` : Flag events as deleted without losing them, support undelete for when we need forensic investigation.
* `startRestServer` : Built-in RESTful endpoints for CRUD, query, TTL management, and admin operations so we can drop this in as a microservice.

