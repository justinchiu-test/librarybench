# The Task

I am a healthcare data architect. I want to securely route medical device events and patient vital signs, ensure compliance with encryption mandates, audit and replay streams for investigations, dynamically tune policies, and integrate custom analytics modules. This code repository provides a compliant, resilient event bus for clinical systems.

# The Requirements

* `<subscribeWildcard>` : Support `*` and `#` wildcards to subscribe to device types, wards, or hospital domains.
* `<routeToDeadLetterQueue>` : Divert problematic or repeatedly failing messages (e.g., missing fields) to a dead-letter topic for manual review.
* `<encryptEvent>` : Encrypt all PHI in transit and at rest using pluggable crypto modules to meet HIPAA/GDPR requirements.
* `<applyBackpressure>` : Enforce queue-size limits with configurable policies (block, drop oldest, reject) to protect downstream EHR systems.
* `<registerSerializer>` : Provide hooks for HL7/FHIR serializers or custom JSON/Protobuf formats for interoperability.
* `<batchPublish>` : Batch clinical updates or device metrics for efficient storage and downstream processing.
* `<updateConfigAtRuntime>` : Dynamically adjust backpressure settings, thread-pool sizes, timeouts, and filters via a central API without redeploying.
* `<clusterDeploy>` : Run in a multi-node cluster with leader election and data replication to ensure continuous operation in emergencies.
* `<persistAndReplay>` : Persist events for audit trails and replay streams for incident investigations or clinical audit.
* `<registerExtension>` : Offer a plugin interface for custom dispatch rules, quality-control middleware, or alternative persistence backends.

