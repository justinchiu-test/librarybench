# The Task

I am Charlie, an indie mobile game developer. I want to track player progress, inventory, and achievements in a local JSON store, sync up server‐side, and roll back corrupted save files after crashes. This code repository gives me an embedded microservice with robust versioning, atomic writes, and flexible hooks.

# The Requirements

* `restful_api` : Local HTTP endpoints for creating player profiles, fetching leaderboards, and administering game settings.
* `versioning` : Automatic save‐state history so players can revert to earlier progress if a file gets corrupted.
* `batch_upsert` : Bulk insert or update multiple player stats or inventory items in one network round trip, with transactional safety.
* `encryption_at_rest` : AES-256 encryption of local JSON files to prevent cheat tools from tampering with save data.
* `update_operation` : Merge new inventory items into existing records without overwriting the entire player document.
* `metrics_monitoring` : Expose counters for save/load latencies and index hit rates so I can profile performance on low‐end devices.
* `soft_deletes` : Mark obsolete quest states as deleted for future reference, with options to undelete if the player changes their mind.
* `optional_journaling` : Write-ahead log to recover from mid‐save crashes or roll back to a consistent game state.
* `atomic_file_persistence` : Use atomic rename ensures no partial save files, even if the app crashes during write.
* `transformation_hooks` : Pre-write hooks to validate game data consistency and post-write hooks to sync cloud backups.