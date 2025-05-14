# The Task

I am an IoT Developer. I want to schedule firmware updates, telemetry uploads, and diagnostics across thousands of devices, driven by time or incoming messages. This code repository will handle the complexity of distributed triggers and stateful execution.

# The Requirements

* `trackJobStats()` : Keep statistics on update jobs, telemetry batch counts, success/failure rates, and last-run logs.  
* `setTimezone()` : Coordinate maintenance windows in devices’ local timezones, including correct DST handling.  
* `onEventTrigger()` : Launch diagnostics on incoming MQTT topics, CoAP signals, or HTTP webhooks from edge devices.  
* `addTagMetadata()` : Tag jobs by device type, firmware version, region, or custom metadata for targeted rollouts.  
* `getNextRunTime()` : Programmatically query next update window or telemetry pull for each device group.  
* `shutdownGracefully()` : Signal the scheduler to stop new tasks before rolling out core system upgrades.  
* `pauseTasks()` : Pause non-urgent telemetry uploads during peak network hours, then resume in off-peak.  
* `enableOverlapLocking()` : Ensure only one firmware-flash job per device at a time to prevent bricking.  
* `persistentStorage()` : Use Redis or SQLite to persist job definitions and in-flight state across gateway restarts.  
* `retryStrategy()` : Retry failed device communications with configurable counts, exponential backoff, and randomized jitter.  
