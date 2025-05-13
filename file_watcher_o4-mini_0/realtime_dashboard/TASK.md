# The Task

I am a data engineer building a real-time analytics dashboard that visualizes file activity across our shared storage. I want to capture each file event, enrich it with metadata (user, size, timestamp), and feed it into Kafka for downstream processing. This code repository is my lightweight, async file-watching core that plugs into our streaming pipeline.

# The Requirements

* `LoggingSupport` : Fine-grained logger configuration to route debug and operational logs to console, rotating files, or Graylog.
* `WebhookIntegration` : Post JSON events to a local HTTP-to-Kafka bridge or custom ingestion endpoint.
* `DynamicFilterRules` : Adapt include/exclude patterns at runtime based on traffic, omitting high-volume temp files without restarts.
* `HighLevelEventDetection` : Emit clear create, modify, delete, and move events for metric calculations and anomaly detection.
* `CrossPlatformConsistency` : Consistent event semantics on Windows file shares, Linux NAS mounts, and macOS AFP/SMB shares.
* `CLIInterface` : CLI mode for quick local demos and load-testing workflows.
* `AsyncIOAPI` : Fully async interface to integrate with our asyncio-based ingestion service for back-pressure support.
* `RecursiveDirectoryWatch` : Watch multiple root paths recursively while honoring include/exclude rules to limit event storm.
* `ResilientErrorHandling` : Automatic retry with backoff plus hooks to log or alert on persistent permission or I/O errors.
* `InlineDiffs` : Attach inline diffs for text file updates so analytics can visualize change magnitude and content drift.
