# The Task

I am a Site Reliability Engineer. I want to be able to monitor, scale, and recover our event-driven platform without downtime. This code repository provides all the hooks and controls I need to keep our event bus healthy, balanced, traceable, and secure in production.

# The Requirements

* `reportHealth()`            : expose built-in endpoints for thread-pool status, queue depths, handler counts  
* `balanceLoad()`             : distribute work across multiple worker threads or instances for optimal throughput  
* `propagateContext()`        : automatically carry MDC, tracing spans, and security principals across threads and async tasks  
* `registerSerializer()`      : plug in custom payload codecs (JSON, Protobuf, Avro) for event encoding/decoding  
* `persistEvents()`           : optionally write events to disk or database for audit, replay, and rollback  
* `publishSync()`             : allow synchronous publishing on the current thread for deterministic ordering  
* `updateConfig()`            : change backpressure policies, timeouts, and thread-pool sizes at runtime via API or config store  
* `registerExtension()`       : load custom dispatch strategies, middleware, and queue implementations dynamically  
* `authenticate()`            : enforce ACLs or token checks so only authorized clients can publish/subscribe  
* `handleErrors()`            : capture handler exceptions, trigger exponential-backoff retries, and dead-letter after max attempts  
