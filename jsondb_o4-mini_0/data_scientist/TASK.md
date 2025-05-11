# The Task

I am a data scientist running ephemeral experiments on customer behavior. I want a lightweight store to snapshot results, index parameters, and expire old runs automatically. This code repository lets me spin up ad-hoc stores per experiment.

# The Requirements

* `setTTL` : Auto-purge experiment results older than the configured window (e.g. one week).
* `createIndex` : Maintain in-memory indexes on parameter combos for sub-millisecond filtering.
* `encryptAtRest` : AES-256 encryption of experiment metadata and result sets on disk.
* `enforceSchema` : Optional JSON Schema to validate experiment input and output structure.
* `registerPlugin` : Add custom plugins for data normalization, sampling, or replication to S3.
* `batchUpsert` : Bulk insert results from large vectorized runs in one atomic operation.
* `persistAtomically` : Use atomic write strategy to avoid data loss during compute node crashes.
* `delete` : Drop data by experimentID or parameter ranges, with filter-based deletion.
* `softDelete` : Flag experiment runs as “retired” so I can restore if I realize I need old data.
* `startRestServer` : Quick-launch REST API to hook Jupyter notebooks and dashboards into my dataset.

