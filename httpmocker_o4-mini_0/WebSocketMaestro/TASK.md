# The Task

I am a real-time systems engineer building a multiplayer game backend. I want to be able to mock match-making, chat channels and live game state updates over WebSockets, while also simulating various HTTP-based auth and matchmaking endpoints. This code repository gives me a unified HTTP+WS mock environment.

# The Requirements

* `startRequestRecording` : Log both HTTP and WebSocket handshake requests for debugging.  
* `httpClient.get/post/put/delete` : Call auth, matchmaking or leaderboard REST endpoints as needed.  
* `simulateError` : Force HTTP auth failures or break WS frames mid-stream.  
* `assertHeader` : Verify JWTs, game-session tokens and custom WS subprotocol headers.  
* `registerEndpoint` : Stub match-making REST APIs and scoreboard queries.  
* `configureCORS` : Handle browser-based WS and XHR CORS requirements for joint testing.  
* `mockWebSocket` : Spawn game channels, broadcast messages, handle pings/pongs and simulate disconnects.  
* `setRetryPolicy` : Retry REST calls or WS reconnect with exponential backoff.  
* `addDynamicCallback` : Generate live game state diffs or chat bot responses based on incoming messages.  
* `assertRequestBody` : Validate real-time commands (JSON moves, chat payloads) against custom rules.
