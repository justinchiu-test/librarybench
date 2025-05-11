# The Task

I am a quantitative trading engineer. I want to be able to process market ticks and trade signals with sub-millisecond latency, handle overloads gracefully, ensure secure and reliable delivery, and support on-the-fly tuning and seamless failover. This code repository underpins our real-time trading platform with a pluggable, high-throughput event bus that meets these needs.

# The Requirements

* `<subscribeWildcard>` : Support single-level (`*`) and multi-level (`#`) wildcard subscriptions to flexibly capture instrument or market segment streams.
* `<routeToDeadLetterQueue>` : Route orders or market data messages that repeatedly fail delivery into a dead-letter topic for post-mortem analysis.
* `<encryptEvent>` : Encrypt event payloads in transit and at rest using pluggable crypto modules to protect sensitive trading algorithms and PII.
* `<applyBackpressure>` : Enforce queue-size limits and configure backpressure policies (block, drop oldest, reject) to throttle bursts in tick data.
* `<registerSerializer>` : Allow custom serializers/deserializers (e.g., JSON for logs, Protobuf for feeds) for consistent payload encoding across services.
* `<batchPublish>` : Aggregate trade instructions or market updates into batches to reduce network overhead and maximize throughput.
* `<updateConfigAtRuntime>` : Dynamically adjust backpressure thresholds, timeouts, thread-pool sizes, and topic filters via a centralized API during live trading.
* `<clusterDeploy>` : Run the event bus in a multi-node in-memory cluster with leader election and data replication to ensure zero-downtime trading.
* `<persistAndReplay>` : Persist events to disk or a database and replay streams for backtesting strategies or debugging execution anomalies.
* `<registerExtension>` : Provide a plugin interface for custom dispatch strategies, risk-check middleware, or alternative queue implementations.

