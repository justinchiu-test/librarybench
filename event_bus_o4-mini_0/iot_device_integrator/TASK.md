# The Task

I am an IoT device integrator. I want to ingest telemetry from thousands of sensors, schedule firmware upgrade events, isolate malfunctioning devices, and ensure context (device-ID, location) is carried through. This code repository is my local and edge event bus solution that scales from gateways to cloud.

# The Requirements

* `scheduleDelivery(topic, event, delayMs)` : push firmware upgrade commands or maintenance pings at scheduled intervals  
* `routeToDeadLetterQueue(topic, event)` : divert telemetry that fails parsing or crosses threshold errors into a dead-letter queue for offline investigation  
* `subscribeWithWildcard(pattern, handler)` : handle device streams like `device.*.telemetry` or `gateway.#.status` with a single subscription  
* `ackEvent(eventId)` : acknowledge sensor readings only after they pass validation and storage stages  
* `registerErrorHook(scope, callback)` : attach callbacks to catch, log or notify on dispatch errors per gateway or globally  
* `publishSync(topic, event)` : deliver critical heartbeat signals inline for edge scenarios where threads share a memory bus  
* `publishBatch(events)` : batch sparse telemetry points to conserve bandwidth and improve throughput  
* `propagateContext(ctx)` : carry device metadata (IDs, firmware version, geographic tags) through every handler and downstream adapter  
* `setRetryPolicy(topic, policyOptions)` : configure retry intervals for flaky radio links or intermittent cloud gateways  
* `registerPlugin(pluginModule)` : add custom protocol adapters (e.g., MQTT, CoAP), encryption layers or specialized parsers  
