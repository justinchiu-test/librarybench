# The Task

I am a game developer coordinating real-time in-game events. I want to schedule power-ups, handle player actions with ack/retry semantics, pattern-match event types, and plugin in new transports for analytics or voice chat. This code repository is the backbone for my server-side and client-side event orchestration.

# The Requirements

* `scheduleDelivery(topic, event, delayMs)` : spawn timed in-game events like “doubleXPStart” or “bossSpawn” after a countdown  
* `routeToDeadLetterQueue(topic, event)` : redirect malformed or repeatedly failing actions (e.g., invalid move commands) to a dead-letter channel for review  
* `subscribeWithWildcard(pattern, handler)` : subscribe to dynamic event streams such as `player.*.move` or `zone.#.update`  
* `ackEvent(eventId)` : confirm that critical actions like “purchaseSkin” or “unlockAchievement” have been processed before next state transition  
* `registerErrorHook(scope, callback)` : handle exceptions globally or per-subscription (e.g., physics engine callbacks) to keep the game loop healthy  
* `publishSync(topic, event)` : deliver high-priority, low-latency calls (e.g., collision resolution) synchronously on the same thread  
* `publishBatch(events)` : bundle chat messages or leaderboard updates into batches to optimize network traffic  
* `propagateContext(ctx)` : carry player IDs, session tokens and region info through each layer for telemetry and personalization  
* `setRetryPolicy(topic, policyOptions)` : define retry strategies for transient network drops between client and server  
* `registerPlugin(pluginModule)` : extend the bus with new transports (UDP voice chat), custom serializers (protobuf), or AI-driven moderation hooks  
