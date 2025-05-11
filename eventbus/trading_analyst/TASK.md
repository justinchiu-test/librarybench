# The Task

I am a quant trader building a low-latency event bus for market data, signals, and order execution feeds. I want strict schema checks, encryption for sensitive signals, microsecond-level tracing, and auto-generated stubs to wire up strategies in Java and C++. This code repository delivers a high-performance, type-safe, and secure event bus optimized for HFT and analytics.

# The Requirements

* `<generateStubs>`        : Produce C++, Java, and Python client code with inline API docs for each market topic.  
* `<encryptPayload>`       : Use pluggable crypto (TLS, hardware HSM) to guard trade signals and PII.  
* `<registerSerializer>`   : Optimize Protobuf and flatbuffers serializers/deserializers for sub-microsecond encode/decode.  
* `<authenticateActor>`    : Token-based and PKI authentication so only approved algos and gateways connect.  
* `<propagateContext>`     : Tag events with high-resolution timestamps, correlation IDs, and trace spans for latency profiling.  
* `<balanceLoad>`          : Distribute incoming ticks across multiple handler threads/pools for smooth ingestion.  
* `<validateSchema>`       : Enforce strict Avro/Protobuf schemas to prevent bad data in backtesting and live strategies.  
* `<controlBackpressure>`  : Circuit-breaker style backpressure (block, drop oldest) under extreme market bursts.  
* `<setupClustering>`      : Geo-distributed broker clusters with leader election and zero-down-time failover.  
* `<exposeMetrics>`        : Expose Prometheus histograms, JMX counters for event rates, queue latencies, and handler runtimes.  
