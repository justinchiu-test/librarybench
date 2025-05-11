# The Task

I am an IoT engineer building a telemetry network for thousands of edge sensors. I want to be able to push encrypted readings, evolve schemas over time, and ensure the broker can flex under intermittent connectivity and constrained devices. This code repository provides an extensible event bus with pluggable serialization, secure transport, and backpressure handling tailored for IoT.

# The Requirements

* `<generateStubs>`        : Auto-generate client libraries and API docs so firmware teams can integrate with zero manual work.  
* `<encryptPayload>`       : Encrypt sensor data in transit and at rest using swap-in crypto modules for hardware security modules.  
* `<registerSerializer>`   : Plug in CBOR, Protobuf, or custom binary serializers for compact message formats.  
* `<authorizeDevice>`      : Token-based device authentication and topic ACLs so only approved sensors can publish.  
* `<propagateContext>`     : Carry device metadata (location, firmware version) across event flows and into logs/traces.  
* `<balanceLoad>`          : Spread incoming telemetry across a pool of handlers to avoid hot spots.  
* `<validateSchema>`       : Validate payloads against evolving JSON Schema or Avro definitions before persistence.  
* `<controlBackpressure>`  : Buffer limits and drop-oldest policy when the gateway is overloaded.  
* `<setupClustering>`      : Enable multi-node brokers with failover for gateway farm resilience.  
* `<exposeMetrics>`        : Push event counts, queue lengths, and processing latencies to Prometheus for dashboarding.  
