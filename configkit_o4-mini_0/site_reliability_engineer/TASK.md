# The Task

I am an SRE responsible for service uptime and performance tuning. I need to manage layered thresholds, circuit‐breaker rules, and alerting parameters across dev, QA, and prod. I also need to catch misconfigurations before they hurt availability and allow on‐the‐fly tuning via CLI or UI hooks. This code repository is my reliability toolkit.

# The Requirements

* `DefaultFallback` : provision safe thresholds and timeouts out of the box
* `TOMLLoader` : ingest service-level threshold specs from a versioned TOML in GitOps
* `EnvLoader` : allow overrides through `SRE_` env vars injected by CI/CD
* `ArgvLoader` : let `srectl` override things like `circuit_breaker.error_rate` on the command line
* `ConflictReporting` : detect contradictory SLA targets or circular alert rules
* `NestedMerge` : update nested maps of endpoints → alerts but replace full lists of notification channels
* `CustomCoercers` : coerce percentages, rates, and time units into appropriate numeric types
* `CLIConfigGenerator` : auto-generate a `srectl` CLI with flags for every config key
* `ConfigWatcher` : attach a hook to update Prometheus rules when `alert.threshold` changes
* `HotReload` : watch config files so changes propagate to live monitoring without restarting services

