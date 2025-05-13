# The Task

I am a Home Automation Enthusiast. I want to schedule lights, climate controls, and sensor routines based on time, events, or custom tags. This code repository will unify my smart-home scripts with reliability and robust error handling.

# The Requirements

* `trackJobStats()` : Monitor how often each routine runs, success vs. failure (e.g., door lock automation), and runtime metrics.  
* `setTimezone()` : Run “good morning” scenes at 7 AM in my local timezone, adapting for DST shifts automatically.  
* `onEventTrigger()` : Trigger tasks on motion-detection webhooks, doorbell presses, or MQTT messages from IoT sensors.  
* `addTagMetadata()` : Apply tags like “lighting,” “security,” or room-based labels for selective control.  
* `getNextRunTime()` : Display next occurrences of my “turn off porch lights” or “warm up coffee maker” tasks.  
* `shutdownGracefully()` : Temporarily disable all automations when I’m hosting guests or during manual overrides.  
* `pauseTasks()` : Pause energy-saving routines while I’m away on vacation, then resume them upon my return.  
* `enableOverlapLocking()` : Prevent overlapping heat-pump activation routines to avoid redundant cycling.  
* `persistentStorage()` : Store all job definitions in JSON so they persist through hub reboots.  
* `retryStrategy()` : Retry failed commands to devices (e.g., Wi-Fi bulbs) with backoff and jitter to handle flaky connectivity.  
