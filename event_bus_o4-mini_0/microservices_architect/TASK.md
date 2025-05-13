# The Task

I am a microservices infrastructure architect. I want to build a polyglot, pluggable event bus to connect dozens of services, enforce retries, schedule workflows, dead-letter bad messages, and inject observability context. This code repository is my standardized event backbone for decoupled services.

# The Requirements

* `scheduleDelivery(topic, event, delayMs)` : enqueue future workflow steps or saga timeouts (e.g., “payment timeout”) at exact intervals  
* `routeToDeadLetterQueue(topic, event)` : forward events that exceed retry quotas into a DLQ for operational triage  
* `subscribeWithWildcard(pattern, handler)` : enable dynamic service discovery by subscribing to patterns like `service.*.events` or `workflow.#`  
* `ackEvent(eventId)` : let each service explicitly acknowledge events, enabling de-duplication or at-least-once guarantees  
* `registerErrorHook(scope, callback)` : plug in global or per-service error handlers for alerting, deadlocking detection or fallback logic  
* `publishSync(topic, event)` : provide a low-overhead loopback mode for monolithic compatibility tests or initialization code  
* `publishBatch(events)` : atomically emit groups of related events (e.g., “orderCreated” + “inventoryReserved”) to preserve consistency  
* `propagateContext(ctx)` : propagate tenant IDs, correlation IDs and authorization claims through service boundaries  
* `setRetryPolicy(topic, policyOptions)` : configure fixed, exponential, or custom backoff for each channel depending on downstream SLAs  
* `registerPlugin(pluginModule)` : define extension points for custom serializers, transports (AMQP, gRPC), tracing middleware or security adapters  
