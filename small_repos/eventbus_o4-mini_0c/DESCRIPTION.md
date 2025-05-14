# EventBus

## Purpose and Motivation
EventBus is a publish/subscribe dispatcher for decoupling components in a single process. It allows you to register handlers for named events or topics and deliver payloads synchronously or asynchronously. Its flexible filtering and middleware hooks let you insert logging, throttling, or transformations on the fly. Perfect for building modular applications, plugins, or simple in-process notification systems.

## Core Functionality
- Subscribe/unsubscribe handlers to event topics or types, with optional priority ordering  
- Publish events with arbitrary payloads, either synchronously or on a background thread  
- Predicate-based filtering so handlers only receive matching events  
- Hierarchical topic support (e.g., `user.*`, `user.login`) with wildcard subscriptions  
- Middleware pipeline for pre/post processing, logging, or short-circuiting  
- Backpressure control or queue-size limits for async dispatch  

