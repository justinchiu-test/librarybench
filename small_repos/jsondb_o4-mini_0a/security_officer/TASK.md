# The Task

I am a security compliance officer ensuring our logs and customer data are locked down. I want to integrate a minimal DB that enforces encryption, immutability, and auditable deletes. This code repository will power our internal audit pipeline.

# The Requirements

* `setTTL` : Enforce retention policies automatically—records expire after regulatory window (e.g. 90 days).
* `createIndex` : In-RAM indexes for auditID, userID, and eventSeverity, auto-updated to ensure fast forensic queries.
* `encryptAtRest` : Mandatory AES-256 disk encryption for every JSON file—no plaintext anywhere.
* `enforceSchema` : Strict JSON Schema definitions for audit logs to ensure type safety and required fields.
* `registerPlugin` : Pluggable hooks for custom authentication, tamper-proof logging, or external HSM integration.
* `batchUpsert` : Group writes in secure transactions—either all audit records land or none do.
* `persistAtomically` : Guarantee atomic writes with temp-file + rename to prevent partial-write exploits.
* `delete` : Controlled deletion via query filters, with strict role-based access checks.
* `softDelete` : Mark logs as “archived” before final purge, maintain chain-of-custody until destruction.
* `startRestServer` : Expose a locked-down REST API for internal tooling to query and manage logs under RBAC.

