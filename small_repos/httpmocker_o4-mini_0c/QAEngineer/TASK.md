# The Task

I am a QA automation engineer. I want to be able to test every edge case of our REST API—recording requests, simulating failures, asserting headers and payload schemas, and replaying responses for consistent, reliable test suites. This code repository provides an HTTP mock server and client library to orchestrate all of these scenarios.

# The Requirements

* `startRequestRecording` : Log every incoming request (method, URL, headers, body) for later inspection.  
* `httpClient.get/post/put/delete` : Built-in client methods with customizable headers, query params, timeouts and bodies.  
* `simulateError` : Trigger HTTP errors (5xx), connection resets, timeouts or malformed responses on demand.  
* `assertHeader` : Validate presence, exact values or regex patterns of incoming request headers.  
* `registerEndpoint` : Stub handlers on static or regex paths for GET, POST, PUT, DELETE.  
* `configureCORS` : Auto-respond to pre-flight OPTIONS and inject configurable CORS headers.  
* `mockWebSocket` : Spin up mock WebSocket servers to validate handshake, messages and closing behavior.  
* `setRetryPolicy` : Define client-side automatic retries with exponential or fixed backoff per endpoint.  
* `addDynamicCallback` : Provide custom callbacks to generate real-time, parameterized responses.  
* `assertRequestBody` : Validate JSON bodies against schemas or custom predicate functions.
