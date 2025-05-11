# The Task

I am a distributed systems architect designing our company’s new event-driven backbone. I want to be able to rapidly scaffold, secure, and scale microservice-to-microservice messaging with end-to-end observability and fault tolerance. This code repository unifies code generation, encryption, schema enforcement, clustering, and metrics in a single, pluggable event bus framework.

# The Requirements

* `<generateDocumentation>` : Auto-generate API docs, event stubs, and type-safe client libraries from defined topics and schemas.  
* `<encryptPayload>`       : Encrypt event payloads in transit or at rest using pluggable crypto modules (AES, RSA, custom HSM).  
* `<registerSerializer>`   : Allow custom serializers/deserializers (JSON, Protobuf, Avro) for event payload encoding/decoding.  
* `<authorizeActor>`       : Implement ACLs or token-based checks so only authorized publishers/subscribers may interact with given topics.  
* `<propagateContext>`     : Automatically carry contextual data (MDC logs, tracing spans, security principals) across sync/async boundaries.  
* `<balanceLoad>`          : Distribute event handling across multiple worker threads or handler instances to optimize throughput and fairness.  
* `<validateSchema>`       : Enforce payload structure against JSON Schema, Avro, or Protobuf definitions before dispatching to subscribers.  
* `<controlBackpressure>`  : Enforce queue-size limits, pause or drop events on overload, and configure policies (block, drop oldest, reject).  
* `<setupClustering>`      : Support multi-node in-memory cluster with leader election and data replication for high availability.  
* `<exposeMetrics>`        : Expose counters, gauges, and histograms (via JMX, Prometheus) for published events, queue depths, latencies, and handler execution times.  
