# The Task

I am a security analyst auditing our internal event flows for compliance and anomaly detection.  
I want to tag, log, and route suspicious or malformed events into isolated channels while preserving normal traffic.  
This code repository provides me with hooks for error catching, dead‐lettering, filtering, scheduling, and full traceability.

# The Requirements

* `subscribe(handler)`                : Tap into every event publish to feed our SIEM in real time.  
* `subscribe_once(handler)`           : Fire a “first-seen” audit event only once per unique session or IP.  
* `unsubscribe(subscription_handle)`  : Remove monitoring hooks when the environment is decommissioned.  
* `set_global_error_handler(fn)`      : Catch and log any unhandled exceptions in security-related handlers.  
* `on_error(handler, error_callback)` : Trigger an alert or escalation when a subscriber fails under suspicious conditions.  
* `dead_letter_queue("security_dlq")` : Divert malformed or replayed events into a “security_dlq” for forensic analysis.  
* `publish_delayed(event, delay_secs)`: Schedule throttled replays of suspicious traffic for “late binding” analysis.  
* `with_transaction()`                : Correlate batches of audit logs and only emit if the full audit passes validation.  
* `add_filter(lambda e: not e.authenticated)` : Filter and intercept unauthenticated or malformed events.  
* `attach_logger(security_logger)`    : Log every publish, delivery, subscription change, and exception to a secure audit store.  
* `context_middleware()`              : Propagate user IDs, IP addresses, and session tokens through handlers.  
