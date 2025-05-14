# The Task

I am a DevOps reliability engineer. I want to be able to test our microservices’ resilience by simulating network failures, timeouts, malformed payloads, and CORS misconfigurations. This code repository empowers me to introduce chaos into HTTP and WebSocket traffic in a controlled, repeatable way.

# The Requirements

* `startRequestRecording` : Track all inter-service calls for post-mortem analysis.  
* `httpClient.get/post/put/delete` : Fault-injection-aware client with metrics hooks.  
* `simulateError` : Randomize 5xx, connection resets, latencies or broken payloads.  
* `assertHeader` : Detect missing tracing or correlation headers to ensure observability.  
* `registerEndpoint` : Temporarily hijack service routes or wildcard patterns.  
* `configureCORS` : Inject CORS faults to validate front-door gateways.  
* `mockWebSocket` : Create flaky WS servers with dropped frames or malformed JSON.  
* `setRetryPolicy` : Stress-test backoff strategies under load.  
* `addDynamicCallback` : Script progressive delays, partial responses or token rotations.  
* `assertRequestBody` : Catch malformed or unexpected payloads before they reach real services.
