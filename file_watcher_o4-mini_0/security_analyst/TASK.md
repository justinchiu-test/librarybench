# The Task

I am a security analyst monitoring critical configuration and policy files for unauthorized changes. I want to detect any tampering, provide exact diffs of policy edits, and forward alerts to our SIEM. This code repository delivers a hardened, resilient watcher that works seamlessly across our mixed OS environment.

# The Requirements

* `LoggingSupport` : Strictly controlled log levels and handlers, enabling audit-grade logging to local and remote sinks.
* `WebhookIntegration` : Push security event payloads to our SIEM or Splunk HTTP Event Collector.
* `DynamicFilterRules` : Rapidly include or exclude new policy directories or sensitive paths without downtime.
* `HighLevelEventDetection` : High-fidelity detection of file creation, modification, deletion, and renames for audit trails.
* `CrossPlatformConsistency` : Identical semantics across Windows (Active Directory policies), Linux (SELinux configs), and macOS profiles.
* `CLIInterface` : Kick off targeted watchers manually during incident response from any shell.
* `AsyncIOAPI` : Integrate into our asyncio-based threat sensor and alert dispatcher for efficient event loops.
* `RecursiveDirectoryWatch` : Cover nested config hierarchies under `/etc`, `C:\Windows\System32`, or other policy stores.
* `ResilientErrorHandling` : Backoff and retry on token expiration or transient FS permission errors, with secure callbacks.
* `InlineDiffs` : Include precise line diffs in alerts so operations center analysts can quickly review unauthorized or accidental edits.

