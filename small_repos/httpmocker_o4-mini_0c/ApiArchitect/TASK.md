# The Task

I am an API architect designing a new public RESTful interface. I want to be able to prototype endpoints, test CORS policies, define error contracts, and verify clients adhere to my specs. This code repository lets me stand up a spec‐driven mock server with programmable behaviors.

# The Requirements

* `startRequestRecording` : Log every client invocation to refine endpoint definitions and docs.  
* `httpClient.get/post/put/delete` : Built-in testing client for smoke tests against the mock server.  
* `simulateError` : Emulate 429 rate limits, 5xx service faults, or truncated JSON for resilience testing.  
* `assertHeader` : Enforce required headers like API keys, Content-Type, Accept or custom version tags.  
* `registerEndpoint` : Define static or regex path templates for all HTTP methods.  
* `configureCORS` : Test Access-Control-Allow origins, credentials, headers and methods.  
* `mockWebSocket` : Prototype a real-time subscriptions API over WS.  
* `setRetryPolicy` : Demonstrate client best-practice retry/backoff semantics in example scripts.  
* `addDynamicCallback` : Return hypermedia links, UUIDs or federated responses based on inputs.  
* `assertRequestBody` : Validate POST/PUT payloads against OpenAPI/JSON Schema or lambda checks.
