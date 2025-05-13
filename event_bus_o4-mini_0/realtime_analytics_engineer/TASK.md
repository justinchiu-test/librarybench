# The Task

I am a real-time analytics engineer. I want to ingest, enrich and process high-throughput event streams with precise timing guarantees, error isolation, replayability and observability. This code repository gives me a flexible, reliable event bus to power real-time dashboards, anomaly detectors and time-windowed aggregations.

# The Requirements

* `scheduleDelivery(topic, event, delayMs)` : schedule an analytics trigger or time-window watermark publication after a defined delay  
* `routeToDeadLetterQueue(topic, event)` : automatically reroute events that exhaust retry attempts to a dead-letter channel for post-mortem analysis  
* `subscribeWithWildcard(pattern, handler)` : subscribe to dynamic event families like `metrics.*` or `sensor.{temp,pressure}`  
* `ackEvent(eventId)` : acknowledge successful processing so only unacked events are retried or flagged  
* `registerErrorHook(scope, callback)` : attach global or per-stream error callbacks to capture handler exceptions and metrics  
* `publishSync(topic, event)` : emit control messages (e.g., schema updates) inline on the publisher’s thread for predictability  
* `publishBatch(events)` : group hundreds of small metric events into one atomic batch for network and I/O efficiency  
* `propagateContext(ctx)` : carry request IDs, trace spans and user metadata through middleware and down to handlers  
* `setRetryPolicy(topic, policyOptions)` : configure exponential backoff, fixed intervals or jittered retries per topic  
* `registerPlugin(pluginModule)` : extend the bus with custom serializers (e.g., Avro), transport adapters (e.g., Kafka) or enrichment middleware  
