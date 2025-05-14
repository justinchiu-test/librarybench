# The Task

I am a QA engineer automating end-to-end test runs when any test data or configuration files change. I want to debug my watch definitions without side-effects, inspect historical change events, and plug into our self-hosted GitLab CI. This repository delivers a robust watcher I can script in Python or run from the console to drive tests reliably.

# The Requirements

* `cli_interface` : Launch watchers from a terminal to peek at event streams before integrating them.  
* `dry_run_mode` : Run in a “no-op” simulation so I can verify my patterns won’t accidentally delete or modify anything.  
* `event_history_store` : Query and filter past create/modify/delete events to diagnose flaky test triggers.  
* `symlink_config` : Control whether to follow test data symlinks or skip them to avoid loops.  
* `resilient_error_handling` : Automatically retry on transient file-system permission errors or network share hiccups.  
* `cicd_plugins` : Use the GitLab CI plugin to start test jobs when specs change.  
* `handler_registration` : Attach callbacks for file create events to spin up fresh test containers.  
* `hidden_file_filter` : Exclude dot-files or backup files so tests only run on real spec changes.  
* `async_io_api` : Integrate watchers into our asyncio-based test harness for parallel execution.  
* `throttling_control` : Debounce bursts of small temp-file writes from IDEs to avoid test storm.  
