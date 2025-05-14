# The Task

I am a Security Auditor tasked with ensuring no unapproved modifications occur in sensitive codebases. I want fine-grained visibility into file-level changes, cryptographic verification, and tamper-proof logs accessible via API. This code repository gives me continuous monitoring, detailed audit trails, and the ability to dynamically whitelist or blacklist paths.

# The Requirements

* `snapshotDiff`       : Periodically capture full directory states and compute diffs to detect missing or unexpected files.
* `fileHashComparison` : Use SHA-256 hashes to cryptographically verify file integrity at each scan.
* `dynamicFilterRules` : Instantly apply new include/exclude rules when I discover suspicious patterns, without downtime.
* `loggingSupport`     : Enforce immutable, append-only logs, choose audit-grade formats, and ship to a SIEM.
* `configFileSupport`  : Load secure watcher configs from versioned TOML or YAML, with strict schema validation.
* `gitignoreParsing`   : Honor `.gitignore` so we don’t miss exclusions already vetted by development teams.
* `restfulAPI`         : Fetch real-time event feeds, query historical data, and automate incident response workflows.
* `eventBatching`      : Aggregate related file events into single records for efficient forensic analysis.
* `cliInterface`       : Launch quick audits from my terminal on compromised hosts or remote environments.
* `hiddenFileFilter`   : Filter out system or hidden files to reduce noise and focus on critical assets.

