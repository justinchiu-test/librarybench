# The Task

I am an e-commerce platform architect. I want to orchestrate order lifecycle events (cart, payment, shipment) reliably, retry transient failures, schedule promotional pushes, and isolate faulty workflows. This code repository provides a robust, multi-tenant event backbone for my microservices suite.

# The Requirements

* `scheduleDelivery(topic, event, delayMs)` : defer “abandonedCartReminder” or “flashSaleStart” notifications to precise future times  
* `routeToDeadLetterQueue(topic, event)` : route failed “paymentConfirmed” or “inventoryUpdated” events after N retries into a dead-letter queue for manual review  
* `subscribeWithWildcard(pattern, handler)` : listen on patterns like `order.*`, `inventory.#` or `user.{login,profile}` to simplify dynamic service registration  
* `ackEvent(eventId)` : confirm successful handling in billing, shipping or accounting services before removing from in-flight  
* `registerErrorHook(scope, callback)` : log or alert on per-service or global dispatch errors (e.g., payment gateway timeouts)  
* `publishSync(topic, event)` : synchronously emit mission-critical calls (e.g., address validation) where async delivery is too risky  
* `publishBatch(events)` : submit bulk order status updates in one go to minimize latency and transactional gaps  
* `propagateContext(ctx)` : forward customer session IDs, tenant metadata and trace context for end-to-end observability  
* `setRetryPolicy(topic, policyOptions)` : tune retry backoff for flaky downstream systems like external fraud checks or warehouse APIs  
* `registerPlugin(pluginModule)` : plug in custom middleware (e.g., GDPR-compliance scrubbing), serializers (e.g., JSON-schema) or monitoring adapters  
