# The Task

I am a Social Media Manager planning and automating content across multiple channels. I want to schedule posts, images, and stories at optimal times every day—skip weekends or holidays, get notified on posting errors, tag campaigns, see metrics on failures and queue health, and optionally use asyncio for batch uploads to APIs. This code repository will be my one-stop post-scheduler and monitoring tool.

# The Requirements

* `run_coroutine`             : Batch upload images and videos to social platforms asynchronously via asyncio.  
* `register_error_handler`    : Hook into post‐failure events to log errors and alert the team via Slack or email.  
* `schedule_daily`            : Set up daily posting times (e.g., 9 am, 12 pm, 6 pm) for each channel.  
* `send_notification`         : Send notifications on post success, failure, or retry via Slack, email, or webhooks.  
* `start_health_check`        : Expose scheduler liveness/readiness endpoints for Docker or Kubernetes deployment.  
* `configure_calendar_exclusions` : Automatically skip posts on weekends, holidays, or custom brand blackout dates.  
* `add_tag`                   : Tag tasks with campaign names like `“SpringSale”` or content types like `“video”`.  
* `define_dependency`         : Ensure that teaser posts go live only after confirmation of creative assets.  
* `expose_metrics`            : Collect and export metrics—post durations, queue length, success/failure counts—for Prometheus.  
* `schedule_cron`             : Use cron expressions for end-of-month reporting or ad-hoc flash sales.  
