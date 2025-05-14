# The Task

I am a backend QA engineer responsible for full-stack integration testing. I want to create a suite of mocks that can verify request headers, bodies, auth flows, rate limits, and even WebSocket streams, so I can automate our contract tests against every backend component without hitting production or staging. This repository is my one-stop shop for programmable HTTP/WebSocket scenarios.

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
