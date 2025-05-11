# The Task

I am a mobile game developer building an offline-first RPG. I want local JSON storage for player profiles, inventories, and leaderboard snapshots with version history, auto-expire demo accounts, and a live feed to update the UI. Eventually I’ll sync to cloud storage backends and need encryption for user data. This code repository is my lightweight embedded DB.

# The Requirements

* `trackVersions` : Save every state of player documents so I can rollback or diff past inventory changes  
* `setTTL` : Demo or guest accounts automatically expire after N days to free up local space  
* `streamChanges` : Push real-time change events to the in-game UI for leaderboard updates  
* `updateDocument` : Patch any part of a profile or do a full replace with merge semantics  
* `backupRestore` : Create local snapshots before major updates and restore when the player taps “Revert”  
* `controlConcurrency` : Ensure thread-safe writes from multiple game subsystems (network, UI, background save)  
* `encryptAtRest` : AES-256 encrypt per-user JSON to protect personal data on stolen devices  
* `batchUpsert` : Atomically insert or update dozens of item records in one go when loading a new level  
* `registerPlugin` : Hook in custom analytics, compression, or ad-network logging modules  
* `setStorageBackend` : Switch transparently between in-memory for tests, file system on mobile, or remote S3 for sync  
