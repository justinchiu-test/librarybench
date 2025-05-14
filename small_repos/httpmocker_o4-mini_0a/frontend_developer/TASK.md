# The Task

I am a frontend developer building an SPA that relies on multiple microservices. I want to be able to spin up mock endpoints that behave exactly like our real APIs—complete with auth checks, CORS, streaming, and real-time events—so I can develop UI features offline and write reliable integration tests. This code repository gives me a powerful, runtime-reloadable HTTP/WebSocket mocking layer that covers every corner case.

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
