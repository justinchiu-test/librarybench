# The Task

I am a marketing operations specialist orchestrating email campaigns, SMS alerts, and social-media posts across multiple regions. I want a centralized scheduler to handle recurring promotions, conditional follow-ups, and rate limits, with real-time visibility into campaign progress. This code repository offers a flexible, pluggable engine I can integrate into our CRM and CDP.

# The Requirements

* `DistributedExecution` : Run redundant scheduler instances in multiple data centers so campaign tasks never get missed during failovers.  
* `PrePostHooks` : Load customer context before each message send and clean up tracking cookies or temp assets afterward.  
* `ConcurrencyLimits` : Enforce regional rate limits per channel (email/SMS) and global send caps to comply with provider quotas.  
* `WorkflowChaining` : Build sequences like “send welcome email → wait 3 days → send promotion → if unopened, resend.”  
* `MonitoringDashboard` : Watch live campaign metrics, scheduled send windows, history of deliveries, bounces, and engagement logs.  
* `DockerK8sSupport` : Deploy schedulers in our Kubernetes cluster with Helm for blue/green updates.  
* `CronExpressionSupport` : Schedule weekly newsletters, monthly loyalty rewards, and daily SMS reminders via cron expressions.  
* `JitterAndDriftCorrection` : Stagger send times across regions to avoid bursts and correct schedule drift after time-zone changes.  
* `RecurringTasks` : Set up ongoing nurture series that requeue themselves after each send cycle.  
* `PluginArchitecture` : Add custom serializer for our internal message format and implement a custom transport for our in-house messaging API.  
