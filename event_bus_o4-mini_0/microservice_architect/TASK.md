# The Task

I am a microservice architect designing distributed, event-driven systems.  
I want to be able to route, monitor, and recover events across services with full observability and reliability guarantees.  
This code repository gives me a pluggable, in-process event bus that supports advanced error handling, scheduling, filtering, and transactional publishes.

# The Requirements

* `subscribe(handler)`                : Register synchronous callback functions to receive events as soon as they’re published.  
* `subscribe_once(handler)`           : Create one-shot subscriptions that auto-unsubscribe after handling the next event.  
* `unsubscribe(subscription_handle)`  : Remove a subscriber by handle at any time to stop future deliveries.  
* `set_global_error_handler(fn)`      : Install a global callback for catching exceptions thrown during any dispatch.  
* `on_error(handler, error_callback)` : Attach a per-subscriber callback to handle errors during that subscriber’s dispatch.  
* `dead_letter_queue(channel_name)`   : Auto-route events to a dead‐letter channel after N retries or fatal errors.  
* `publish_delayed(event, delay_secs)`: Schedule an event for future delivery (e.g. “in 5 seconds”).  
* `with_transaction()`                : Batch multiple `publish()` calls and dispatch only if the block completes without exceptions.  
* `add_filter(predicate_fn)`          : Register filtering middleware that drops events not satisfying the predicate.  
* `attach_logger(logger)`             : Hook into publishes, deliveries, errors, and subscription changes for auditing and metrics.  
* `context_middleware()`              : Automatically propagate metadata (request IDs, trace IDs, user info) through handlers.  
