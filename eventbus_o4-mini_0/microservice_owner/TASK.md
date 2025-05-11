# The Task

I am a Backend Microservices Developer. I want to be able to plug in a flexible event bus into my service, customize serialization, and rely on built-in monitoring and retry logic. This code repository gives me everything in a single library so I can focus on business logic, not plumbing.

# The Requirements

* `reportHealth()`            : CLI or HTTP endpoints showing thread pools, queue metrics, and handler counts  
* `balanceLoad()`             : round-robin or weighted dispatch to spread events across my service replicas  
* `propagateContext()`        : carry trace IDs, user IDs, and security credentials through sync/async boundaries  
* `registerSerializer()`      : add my own JSON, Protobuf, or Avro serializers for domain-specific payloads  
* `persistEvents()`           : toggle event persistence and replay mode for development and debugging  
* `publishSync()`             : send critical events immediately on the service thread for simpler error semantics  
* `updateConfig()`            : live-edit timeouts, queue limits, backpressure rules, and custom filters via REST API  
* `registerExtension()`       : hook in custom pipeline stages or implement an alternate in-memory queue  
* `authenticate()`            : define topic-level ACLs or OAuth2 tokens so only specific microservices can interact  
* `handleErrors()`            : automatically retry failed handlers with exponential backoff and flag poison messages  
