# retry_backoff

## Purpose and Motivation
This library provides a flexible, policy-driven mechanism for retrying operations that may fail intermittently (e.g., network calls, I/O, transient errors). By centralizing retry logic and backoff strategies, it helps developers avoid scattered boilerplate and ensure consistent error-handling across projects. It is designed to be highly configurable so that users can pick between fixed, exponential, or custom backoff schedules and plug in logging, metrics hooks, or cancellation policies. The library can be used in both synchronous and threaded contexts.  
Potential use cases include HTTP request retries, database reconnections, and retrying any idempotent function call.  
Extension points: custom backoff generators, pluggable stop conditions, user-defined jitter strategies, or integration with event loops.

## Core Functionality
- A decorator and context-manager API for wrapping arbitrary callables with retry logic  
- Built-in backoff strategies: fixed delay, exponential backoff, full jitter, and capped backoff  
- Configurable stop conditions: max attempts, deadline timers, or custom predicates  
- Hooks for before/after each attempt for logging, metrics, or side-effects  
- Support for synchronous and threaded execution models (using `threading.Event` for cancellation)  
- Pluggable strategy interface to register new backoff or stop-condition classes  

