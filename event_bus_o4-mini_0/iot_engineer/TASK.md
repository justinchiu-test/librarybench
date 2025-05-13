# The Task

I am an IoT engineer building a fleet management gateway.  
I want to ingest sensor data, retry transient failures, and route bad messages into quarantine.  
This code repository provides an embedded event bus with hooks for errors, DLQ, filters, scheduling, and context metadata.

# The Requirements

* `subscribe(handler)`                : Process telemetry as soon as devices report temperature, GPS, or heartbeat.  
* `subscribe_once(handler)`           : Run firmware-update check only once when a new device registers.  
* `unsubscribe(subscription_handle)`  : Unenroll devices or modules dynamically to free resources.  
* `set_global_error_handler(fn)`      : Catch any unhandled exception in subscribers and alert the ops team.  
* `on_error(handler, error_callback)` : Perform per-device error recovery (e.g. circuit breaker) when dispatch fails.  
* `dead_letter_queue("quarantine")`   : Quarantine malformed or consistently-failing events for offline analysis.  
* `publish_delayed(event, delay_secs)`: Schedule commands or maintenance alerts to run at off-peak hours.  
* `with_transaction()`                : Batch configuration updates to many devices and apply only if all succeed.  
* `add_filter(lambda e: e.sensor_type=="temperature")`: Drop irrelevant sensor data before processing.  
* `attach_logger(iot_logger)`         : Log publishes, deliveries, errors, and subscription changes in a central dashboard.  
* `context_middleware()`              : Tag each event with device ID, firmware version, and request trace.  
