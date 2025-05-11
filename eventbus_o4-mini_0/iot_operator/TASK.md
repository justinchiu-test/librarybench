# The Task

I am an IoT platform operator. I want to be able to onboard and manage millions of devices, filter and dispatch telemetry streams efficiently, secure sensitive device data, throttle spikes, and recover lost messages for diagnostics. This code repository equips me with a flexible, scalable event bus tailored for IoT scenarios.

# The Requirements

* `<subscribeWildcard>` : Use single-level (`*`) and multi-level (`#`) wildcards to subscribe to device groups or entire site hierarchies.
* `<routeToDeadLetterQueue>` : Route malformed or repeatedly undeliverable sensor payloads to a dead-letter topic for manual recovery.
* `<encryptEvent>` : Encrypt sensor data in transit and at rest with pluggable crypto modules to meet security policies.
* `<applyBackpressure>` : Enforce queue-size limits, pause or drop events when capacity is reached, and choose policies (block, drop oldest, reject).
* `<registerSerializer>` : Plug in custom serializers/deserializers (JSON, CBOR, Protobuf) to minimize payload size and ensure interoperability.
* `<batchPublish>` : Batch telemetry messages to optimize network usage across constrained links.
* `<updateConfigAtRuntime>` : Change backpressure policies, timeouts, thread-pool sizes, and topic filters at runtime via a centralized config store.
* `<clusterDeploy>` : Deploy the bus in a multi-node cluster with leader election and data replication to survive node failures.
* `<persistAndReplay>` : Persist events to disk or a database and replay streams for debugging connectivity or firmware issues.
* `<registerExtension>` : Extend the bus with custom device-management middleware or alternative queue backends.

