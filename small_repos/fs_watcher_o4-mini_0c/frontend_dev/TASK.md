# The Task

I am a frontend developer working on a React app. I want my dev server to auto‐reload when I modify JSX, CSS, or asset files, but ignore build artifacts. This code repository offers a pluggable watcher to power hot-reload, linting, and style checks on file change.

# The Requirements

* `start_metrics_endpoint` : stream live metrics (reloads/sec, average reload latency) into my local dashboard  
* `scan_once`              : allow a manual “check everything” command before committing my code  
* `register_plugin`        : hook in custom filters (exclude `dist` folder), ESLint/StyleLint transformers, and Webpack HMR sinks  
* `set_thread_pool_size`   : run linting, style checks, and recompiles in parallel without choking my laptop  
* `configure_logging`      : send detailed debug logs for plugin failures or skipped files  
* `set_handler_timeout`    : kill stuck HMR update handlers after a timeout so my dev server stays responsive  
* `set_throttle_rate`      : debounce rapid typographic edits to avoid unnecessary full rebuilds  
* `generate_change_summary`: show a “Files changed since last build: 8” overlay in the browser console  
* `enable_move_detection`  : detect when I reorganize components so HMR preserves state  
* `add_ignore_rule`        : filter out editor swap files (`.swp`, `~`) and macOS hidden files

