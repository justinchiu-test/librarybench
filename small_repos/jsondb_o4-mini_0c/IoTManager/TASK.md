# The Task

I am an IoT systems manager for a smart-agriculture deployment. I collect sensor readings and actuator commands in a local edge server. I need versioned data, timed roll-off of old readings, a live event stream for our control dashboard, and the ability to swap between in-RAM, SD card, or cloud storage. This code repository is my edge JSON database.

# The Requirements

* `trackVersions` : Keep full history of sensor and actuator JSON messages, with rollback for error investigations  
* `setTTL` : Automatically expire old sensor readings (e.g., >30 days) to conserve local disk  
* `streamChanges` : Publish a live WebSocket stream of changes for our farm-management UI  
* `updateDocument` : Patch device configs or replace entire status documents with merge support  
* `backupRestore` : Periodic backups of the DB folder to USB or remote NFS, with quick restore on failure  
* `controlConcurrency` : Optimistic locking for concurrent writes from multiple edge-compute threads  
* `encryptAtRest` : AES-256 encryption on local SD card to secure sensor data on remote field nodes  
* `batchUpsert` : Bulk upload of hundreds of readings in a single atomic operation for efficient edge sync  
* `registerPlugin` : Add custom compression, replication, or device-health monitoring plugins  
* `setStorageBackend` : Swap between in-memory for tests, local FS on the edge, or S3/Blob for cloud sync  
