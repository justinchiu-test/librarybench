# The Task

I am a QA engineer designing end-to-end test suites for our microservice platform. I want to lock down exactly how the client must send headers, query parameters, JSON payloads, and tokens, then force the server to respond with edge-case delays, 429 status codes, chunked streams, and WebSocket errors. This repo provides all the hooks I need to automate every negative and positive test scenario.

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
