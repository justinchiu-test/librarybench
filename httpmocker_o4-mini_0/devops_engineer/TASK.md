# The Task

I am a DevOps engineer setting up staging and canary environments. I want to embed a lightweight mock server into our deployment pipelines for chaos-testing API failures, rate throttling, chunked transfer delays, and simulated CORS blocks. This repository lets me script and hot-swap mocks on demand without touching production code or container images.

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
