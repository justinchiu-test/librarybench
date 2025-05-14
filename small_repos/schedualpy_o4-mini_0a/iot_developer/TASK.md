# The Task

I am an IoT platform developer integrating thousands of edge devices sending telemetry every minute. I want a robust scheduling system to poll devices, process streams, and run maintenance routines without dropping messages or overwhelming gateways. This code repository powers my device‐management cron, stream backfills, and automated firmware rollouts with full observability and horizontal scaling.

# The Requirements

* `DistributedExecution` : Run multiple scheduler instances across edge sites and the cloud, all consuming from the same queue to guarantee at-least-once execution.  
* `PrePostHooks` : Authenticate with devices before polling, set up SSL tunnels, and clean up stale connections afterward.  
* `ConcurrencyLimits` : Throttle concurrent device pings and stream analytics tasks based on gateway capacity.  
* `WorkflowChaining` : Chain device poll → parse → store → alert pipelines, with conditional retry branches on timeouts.  
* `MonitoringDashboard` : Real-time view of scheduled polls, backlog depth, last‐seen device timestamps, and error rates.  
* `DockerK8sSupport` : Deploy edge and cloud schedulers as Docker containers or via Helm so I can roll out updates safely.  
* `CronExpressionSupport` : Use cron syntax to schedule health checks, nightly backfills, and firmware rollouts.  
* `JitterAndDriftCorrection` : Add random delays to device polling to prevent sudden network spikes, and auto-align schedules after network partitions.  
* `RecurringTasks` : Automatically requeue telemetry backfill jobs after each execution window.  
* `PluginArchitecture` : Plug in custom transports (e.g., MQTT, AMQP) and serializers (e.g., CBOR) to meet IoT standards.  
