# The Task

I am a Site Reliability Engineer. I want to aggregate logs, metrics, and tracing spans from all microservices, filter them flexibly, handle surges gracefully, secure sensitive data, persist streams for post-mortem analysis, and extend pipelines with custom alerting. This code repository powers our observability event bus.

# The Requirements

* `<subscribeWildcard>` : Support single-level (`*`) and multi-level (`#`) wildcards to capture logs or metrics by service, region, or environment.
* `<routeToDeadLetterQueue>` : Route malformed or repeatedly undelivered telemetry messages to a dead-letter topic for root-cause investigation.
* `<encryptEvent>` : Encrypt sensitive log entries and trace data in transit and at rest via pluggable crypto modules.
* `<applyBackpressure>` : Enforce queue-size limits and choose policies (block, drop oldest, reject) to protect downstream storage systems during spikes.
* `<registerSerializer>` : Allow custom serializers/deserializers (JSON, Avro, Protobuf) for integration with diverse observability tools.
* `<batchPublish>` : Batch logs and metrics into bulk uploads to optimize storage API calls.
* `<updateConfigAtRuntime>` : Dynamically tweak backpressure thresholds, timeouts, filters, and thread-pool sizes through a centralized config API.
* `<clusterDeploy>` : Run the bus in a fault-tolerant multi-node cluster with leader election and replication for high availability.
* `<persistAndReplay>` : Persist event streams and replay them for incident diagnostics or compliance audits.
* `<registerExtension>` : Expose a plugin interface for custom enrichment middleware, alerting rules, or alternative queue backends.
