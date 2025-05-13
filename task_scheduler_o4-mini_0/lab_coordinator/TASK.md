# The Task

I am a Research Lab Coordinator. I want to schedule equipment calibrations, data collection scripts, and safety checks on precise intervals or sensor triggers. This code repository will guarantee experiments run on time, with full logging and controlled shutdowns.

# The Requirements

* `trackJobStats()` : Log how many calibration runs, data captures, and safety audits occurred, plus success/failure breakdowns and durations.  
* `setTimezone()` : Align routines with the lab’s local timezone and automatically adapt for DST laboratory periods.  
* `onEventTrigger()` : Start sample processing when sensors report thresholds, or on external triggers from the LIMS.  
* `addTagMetadata()` : Tag tasks by equipment, experiment ID, or priority to filter for daily reports.  
* `getNextRunTime()` : Query the next scheduled maintenance or data-acquisition window for each device.  
* `shutdownGracefully()` : Pause new experiments and optionally let running scripts complete before power-down.  
* `pauseTasks()` : Temporarily suspend non-critical routines (like overnight imaging) and resume after troubleshooting.  
* `enableOverlapLocking()` : Ensure that only one calibration cycle per instrument runs at a time to avoid conflicts.  
* `persistentStorage()` : Persist all job definitions and logs in JSON or SQLite to maintain audit trails across restarts.  
* `retryStrategy()` : Retry flaky instrument commands or network data uploads with configurable retry counts, exponential backoff, and jitter.  
