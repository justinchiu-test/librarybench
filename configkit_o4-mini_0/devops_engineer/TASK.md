# The Task

I am a DevOps engineer managing homogeneous fleets across staging, canary, and production clusters. I want a unified config framework to define defaults, inject environment-specific overrides, detect misconfigurations, and give operators an on-the-fly CLI for emergency tweaks. This code repository is my swiss army knife for all of that.

# The Requirements

* `DefaultFallback` : define one golden copy of defaults and use it everywhere
* `TOMLLoader` : pull in cluster-wide overrides from versioned TOML files in Git
* `EnvLoader` : pick up pod-level variables automatically using a `CLUSTER_` prefix
* `ArgvLoader` : allow `kubectl exec mypod -- --override key=value` to apply an immediate override
* `ConflictReporting` : catch circular or contradictory overrides between staging/canary/prod layers
* `NestedMerge` : merge per-service labels but override entire arrays for sidecar containers
* `CustomCoercers` : coerce resource quantities like “500Mi” or “2Gi” into integer bytes
* `CLIConfigGenerator` : generate a `deployctl` CLI so on-call can adjust timeouts, feature-gates, or rollout percentages
* `ConfigWatcher` : register hooks to trigger rolling restarts when `health.check.interval` gets updated
* `HotReload` : live-reload config in development clusters so I can test changes without a full redeploy

