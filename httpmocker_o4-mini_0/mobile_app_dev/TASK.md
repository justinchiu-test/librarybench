# The Task

I am a mobile app developer working offline on Android and iOS clients. I want a local server that can mimic our backend’s REST and WebSocket behaviors—including auth tokens, rate-limits, CORS quirks, and streaming—so I can test push notifications, live updates, and error states even when the real API is down. This toolkit delivers that complete mocking experience in seconds.

# The Requirements

* `registerEndpoint` : Register handlers using static or regex paths for specific HTTP methods.  
* `assertHeader` : Assert presence, values, or patterns of incoming request headers.  
* `assertBody` : Validate request bodies using JSON schemas or custom predicate functions.  
* `configureCORS` : Configure CORS headers and pre-flight OPTIONS responses.  
* `simulateAuth` : Mock Basic, Digest, or Bearer token authentication flows.  
* `mockWebSocket` : Support mock WebSocket endpoints for testing real-time interactions.  
* `hotReloadHandlers` : Reload or update endpoint definitions at runtime without restarting.  
* `simulateRateLimiting` : Simulate API rate limits with quotas and “Retry-After” headers.  
* `assertQueryParam` : Validate query parameters against expected patterns or values.  
* `simulateChunkedTransfer` : Simulate chunked HTTP transfers for streaming or partial responses.  
