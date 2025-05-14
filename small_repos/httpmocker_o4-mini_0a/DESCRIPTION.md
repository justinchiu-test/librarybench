# HttpMocker

## Purpose and Motivation
HttpMocker provides a simple HTTP server/client pair for testing HTTP-based integrations without external dependencies. Using the standard library’s `http.server` and `urllib.request`, you can define expected endpoints, canned responses, and request assertions. This speeds up unit and integration tests for code that calls REST APIs.

## Core Functionality
- Start/stop a local HTTP server with configurable port and address.
- Register endpoint handlers via path patterns (static or regex) and HTTP methods.
- Define canned responses (status, headers, body) or dynamic response callbacks.
- Record incoming requests for inspection (method, path, headers, payload).
- Client utilities for GET, POST, PUT, DELETE with JSON and form encoding helpers.
- Timeout, retry, and error-simulation hooks to test failure modes.
