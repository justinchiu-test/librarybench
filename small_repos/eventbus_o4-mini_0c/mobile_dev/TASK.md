# The Task

I am a mobile app developer integrating real-time chat and notifications into our iOS/Android clients. I want a type-safe, auto-documented API for publish/subscribe that supports offline buffering, secure channels, and built-in tracing. This code repository acts as a unified event bus SDK for both mobile and server layers.

# The Requirements

* `<generateClientSDK>`    : Auto-generate iOS (Swift) and Android (Kotlin) client libraries with in-app docs.  
* `<encryptPayload>`       : Provide end-to-end encryption of chat messages and notifications.  
* `<registerSerializer>`   : Support JSON, MessagePack, and Protobuf serializers for different payload sizes.  
* `<authenticateUser>`     : OAuth2 token checks and topic ACLs so only logged-in users can publish/subscribe.  
* `<propagateContext>`     : Carry correlation IDs, user IDs, and performance marks through remote calls and callbacks.  
* `<balanceLoad>`          : Throttle or route message handling between local cache and remote service to smooth spikes.  
* `<validateSchema>`       : Enforce JSON Schema on inbound/outbound messages to catch client bugs early.  
* `<controlBackpressure>`  : Queue-size limits on device client side, with configurable drop or block policies.  
* `<setupClustering>`      : Transparent multi-endpoint failover for mobile sync services.  
* `<exposeMetrics>`        : Emit counters and histograms to Firebase or Prometheus (via mobile-friendly endpoints) for request rates and latencies.  
