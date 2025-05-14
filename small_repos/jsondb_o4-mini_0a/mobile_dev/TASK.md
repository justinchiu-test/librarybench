# The Task

I am a mobile app developer building an offline-first journaling app. I want the local database to handle intermittent connectivity, automatic cleanup, and secure storage. This code repository will be embedded in the mobile app and sync with our cloud when online.

# The Requirements

* `setTTL` : Auto-expire drafts older than 30 days, with background sweeper optimized for device resources.
* `createIndex` : Load indexes in memory on startup and maintain them on writes for blazing-fast tag searches.
* `encryptAtRest` : AES-256 encryption of JSON files on device to protect diaries and photos metadata.
* `enforceSchema` : Define custom schema for journal entries, attachments, and metadata to catch bugs early.
* `registerPlugin` : Hook in plugins for conflict resolution, network replication, or image compression.
* `batchUpsert` : Bundle multiple entries and attachments in a single atomic call to avoid partial syncs.
* `persistAtomically` : Write to temp files and atomic rename so a crash during save never corrupts user data.
* `delete` : Provide delete-by-ID or filter—e.g. delete all “draft” entries older than X days.
* `softDelete` : Mark entries deleted in-app, allow “undo delete” UI flow, and purge permanently on user request.
* `startRestServer` : Spin up a tiny local HTTP server for WebView components to talk to the database layer.

