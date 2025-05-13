# fs_watcher

## Purpose and Motivation
A simple file‐system watcher that polls directories for changes to files or subdirectories and dispatches events (create, modify, delete). Unlike heavyweight solutions, this library uses only `os`, `time`, and `threading` modules to provide cross-platform support without extra dependencies. It offers a high-level API to subscribe handlers to path patterns and debounce rapid change bursts.  
Use cases: auto-reload in development servers, syncing local changes, triggering build pipelines on file edits.  
Extension points: custom polling strategies, alternative event batching logic, or integration with async frameworks.

## Core Functionality
- Monitor one or more directories recursively, tracking file metadata via `os.stat`  
- Emit typed events (created, modified, deleted) with timestamp and path information  
- Register and deregister callback handlers with glob-style path patterns  
- Debounce or throttle event streams to avoid callback storms  
- Ability to start/stop watchers in background threads, with clean shutdown  
- Utility functions to snapshot current directory state and diff against new scans

