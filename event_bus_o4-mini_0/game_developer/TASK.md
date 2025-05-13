# The Task

I am a real-time multiplayer game developer building a fast-paced, event-driven server.  
I want to fire game state updates, player actions, and world events with precise control over retries, timeouts, and logging.  
This code repository equips me with a flexible event bus supporting one‐shots, scheduling, dead‐lettering, filtering, and context tracing.

# The Requirements

* `subscribe(handler)`                : Listen for “player_moved”, “shot_fired”, or “powerup_spawned” events immediately.  
* `subscribe_once(handler)`           : Trigger and remove “tutorial_complete” or “first_login” hooks after one event.  
* `unsubscribe(subscription_handle)`  : Cleanly drop obsolete listeners when a match ends or player disconnects.  
* `set_global_error_handler(fn)`      : Catch and log uncaught errors across all game event handlers.  
* `on_error(handler, error_callback)` : Handle failures in specific subsystems (e.g. physics-engine) gracefully.  
* `dead_letter_queue("game_dead")`    : Redirect events that repeatedly crash handlers into a “game_dead” DLQ for inspection.  
* `publish_delayed(event, delay_secs)`: Schedule timed power-ups or respawn events (e.g. after 3 seconds).  
* `with_transaction()`                : Group several state-updates and only broadcast if all succeed.  
* `add_filter(lambda e: e.type == "combat")`: Only deliver combat-related events to the combat-logic subsystem.  
* `attach_logger(game_logger)`        : Record every publish, delivery, subscription change, and error for live debugging.  
* `context_middleware()`              : Carry player session IDs and match IDs through subscribers for tracing.  
