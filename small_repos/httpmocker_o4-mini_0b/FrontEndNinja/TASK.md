# The Task

I am a front-end developer building a new single-page app. I want to be able to work offline, stub out complex backend behavior, and validate that my UI sends correct headers and payloads. This code repository simulates APIs and WebSockets so I can iterate rapidly without a live backend.

# The Requirements

* `startRequestRecording` : Capture UI-originated calls (method, URL, headers, body) to debug interactions.  
* `httpClient.get/post/put/delete` : Simple fetch-style helpers with overrideable defaults and interceptors.  
* `simulateError` : Inject HTTP 5xx, network resets or malformed JSON to test error UI flows.  
* `assertHeader` : Ensure auth tokens or custom headers are included and correctly formatted.  
* `registerEndpoint` : Map URL patterns (strings or regex) to stubbed JSON or HTML responses.  
* `configureCORS` : Add Access-Control headers and handle OPTIONS preflights for local development.  
* `mockWebSocket` : Provide a fake real-time channel for chat, notifications or presence updates.  
* `setRetryPolicy` : Retry failed GETs or POSTs automatically with backoff, so the UI can recover.  
* `addDynamicCallback` : Generate paginated lists, timestamps or random IDs on the fly.  
* `assertRequestBody` : Verify outgoing JSON matches the UI’s data models or validation rules.
