# The Task

I am a Marketing Specialist. I want to automate email blasts, social media posts, and analytics queries based on schedules or user events. This code repository will let me tag campaigns, handle retries on email bounces, and pause sends during high-traffic periods.

# The Requirements

* `trackJobStats()` : Track send counts, open rates, bounces (failures), total send time, and last-run status for each campaign.  
* `setTimezone()` : Schedule email deliveries at optimal local send times, accounting for recipients’ timezones and DST.  
* `onEventTrigger()` : Fire follow-up sequences on webhooks from form submissions, CRM events, or e-commerce triggers.  
* `addTagMetadata()` : Label jobs by campaign name, channel (email/Twitter), or custom fields like audience segment.  
* `getNextRunTime()` : Query when the next batch of email or social post will go live.  
* `shutdownGracefully()` : Halt all outbound traffic in case of a major outage or compliance hold.  
* `pauseTasks()` : Pause specific campaigns mid-flight, then resume when approved.  
* `enableOverlapLocking()` : Prevent duplicate sends by locking on campaign+audience combinations.  
* `persistentStorage()` : Store campaign schedules and state in YAML or SQLite to survive service restarts.  
* `retryStrategy()` : Automatically retry transient email server errors or API rate-limit responses with backoff and jitter.  
