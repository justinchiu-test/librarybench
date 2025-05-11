# The Task

I am Devon, an e‐commerce backend engineer. I want to manage a product catalog service with dynamic pricing, soft‐delete for discontinued items, and bulk updates from supplier feeds. This code repository functions as a JSON DB microservice with high availability, consistency, and operational observability.

# The Requirements

* `restful_api` : CRUD endpoints for product CRUD, price updates, inventory checks, and admin controls.
* `versioning` : Track every product/price change so we can roll back pricing mistakes or supply feed errors.
* `batch_upsert` : Atomically import supplier feed items or bulk price adjustments in one call.
* `encryption_at_rest` : AES-256 encryption on disk to secure sensitive supplier contract data.
* `update_operation` : Merge field‐level updates like stock levels or promotional tags without rewriting the full product record.
* `metrics_monitoring` : Expose Prometheus metrics (API latency, index hit rates, error rates) and a /health endpoint.
* `soft_deletes` : Mark discontinued products as deleted, support undelete for limited time, and automatic purge after season end.
* `optional_journaling` : Write-ahead log for crash recovery and point-in-time rollback if a bad feed ingestion corrupts data.
* `atomic_file_persistence` : Use temp files and atomic renames to guarantee no partial or corrupted JSON files.
* `transformation_hooks` : Pre-write hooks to normalize SKU codes and post-write hooks to update search index and cache.