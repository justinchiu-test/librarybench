# FileWatcher

## Purpose and Motivation
FileWatcher monitors directories or files for changes by periodically polling file metadata (`os.stat`). It raises high-level events (created, modified, deleted, moved) without relying on OS-specific watching APIs. This pure-Python solution is perfect for simple sync tools, auto-reloaders, or testing utilities.

## Core Functionality
- Watch one or more paths (files or directories) with configurable polling interval  
- Detect create/modify/delete/move operations and emit structured event objects  
- Support recursive directory watching with include/exclude filters  
- Allow registering handlers (callbacks) per event type or path pattern  
- Provide a CLI mode to run from command line and print events in real time  
- Extension hooks for alternative backends (e.g., integrating `inotify` or macOS FSEvents)  

