# The Task

I am a DevOps engineer responsible for ensuring the stability and observability of our microservice deployments. I want to be able to watch configuration directories and log folders in real time, automatically surface relevant file changes to our alerting pipeline, and adjust my watch rules on the fly without service restarts. This code repository gives me a battle-tested, cross-platform file-watching library I can plug into our CI/CD and monitoring stack.

# The Requirements

* `LoggingSupport` : Configurable logging subsystem so I can route debug, info, warning, and error messages to console, file, or a custom handler (e.g., Splunk).
* `WebhookIntegration` : Configure HTTP POST endpoints to dispatch change events as webhooks into our PagerDuty or Slack integrations.
* `DynamicFilterRules` : Add or remove include/exclude patterns at runtime when I spin up new environments or retire old ones without restarting the watcher process.
* `HighLevelEventDetection` : Receive structured events for create, modify, delete, and move ops so I can trigger downstream jobs only on the precise file events I care about.
* `CrossPlatformConsistency` : Guarantee that my watch scripts behave identically on developer laptops (macOS), build agents (Linux), and Windows servers.
* `CLIInterface` : Start watchers from the command line in my build pipelines and tail events live for troubleshooting.
* `AsyncIOAPI` : Use asyncio in our Python-based automation to avoid blocking threads while I/O is in flight.
* `RecursiveDirectoryWatch` : Monitor entire config trees or log archives recursively, with include/exclude filtering per directory.
* `ResilientErrorHandling` : Built-in retry and backoff strategies plus error callbacks so transient network or permission errors don’t knock my monitors offline.
* `InlineDiffs` : For every modified text config, get a line-by-line diff in the event payload so I know exactly which setting changed.

