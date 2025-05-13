# EventBus

## Purpose and Motivation
EventBus implements an in-process publish/subscribe mechanism using only Python’s `queue` and `threading` modules. It lets different parts of an application communicate decoupled by sending and receiving typed messages or events. Useful for GUI backends, background workers, or plugin architectures without a full-blown messaging system.

## Core Functionality
- Create named channels to which publishers send messages  
- Subscribe callback functions or coroutine-like handlers to channels  
- Support synchronous (direct call) and threaded (via `queue.Queue` + worker) delivery modes  
- Allow filtering and message transformation middleware layers  
- Provide unsubscribe and one-shot subscription semantics  
- Hooks for custom dispatch strategies (e.g., priority queues or rate-limited delivery)  

