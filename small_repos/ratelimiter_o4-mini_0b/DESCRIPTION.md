# RateLimiter

## Purpose and Motivation
RateLimiter supplies decorators and context managers to control the throughput of function calls or events. It implements classic algorithms like token bucket and leaky bucket using `time`, `threading`, and basic data structures. You can apply global, per-user, or per-resource limits to protect APIs, prevent bursts, or smooth workloads. It’s simple to configure and integrate into any Python codebase without extra dependencies.

## Core Functionality
- Decorators for limiting calls to N per interval, with options to block, sleep, or raise on violation  
- Token bucket and leaky bucket strategies with adjustable refill rates and capacities  
- Per-key scoping (e.g., rate-limit per user ID or IP address)  
- Runtime inspection methods to get current usage, next‐available timestamp, and reset capability  
- Context manager API for manual rate-control around arbitrary code blocks  
- Extension hooks for custom logging, metrics emission, or backoff strategies  
