# The Task

I am an online game server engineer. I want to dispatch player actions, world events, and chat messages across services, support flexible topic patterns, throttle event floods, recover lost packets, and hot-swap dispatch logic without downtime. This code repository underlies our real-time game event bus.

# The Requirements

* `<subscribeWildcard>` : Use single-level (`*`) and multi-level (`#`) wildcards to subscribe to zones, lobbies, or global game channels.
* `<routeToDeadLetterQueue>` : Route malformed or repeatedly undelivered events into a dead-letter topic for diagnostics.
* `<encryptEvent>` : Encrypt game payloads in transit or at rest using pluggable crypto modules to protect user data.
* `<applyBackpressure>` : Enforce queue-size limits with policies (block, drop oldest, reject) to throttle bot attacks or floods.
* `<registerSerializer>` : Allow custom serializers (JSON for logs, Protobuf for binary game data) for efficient network encoding.
* `<batchPublish>` : Batch player state updates or world tick events to reduce synchronization overhead.
* `<updateConfigAtRuntime>` : Change backpressure policies, timeouts, thread-pool sizes, and topic filters via a management console during live play.
* `<clusterDeploy>` : Deploy the event bus in a multi-node cluster with leader election and replication for zero-downtime server scaling.
* `<persistAndReplay>` : Optionally persist events and replay game sessions for debugging, replay, or cheat investigations.
* `<registerExtension>` : Provide a plugin API for custom game-logic middleware, new dispatch strategies, or alternative queue implementations.

