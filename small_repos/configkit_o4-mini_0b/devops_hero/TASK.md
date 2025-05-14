# The Task

I am a DevOps engineer responsible for deploying and monitoring a fleet of microservices. I want to be able to author, merge, visualize, and validate configuration across multiple environments and layers so that I can ship with confidence. This code repository gives me a single unified API and plugin system to handle config from CI/CD pipelines, environment variables, YAML files, and custom sources.

# The Requirements

* `ConfigWatcher`         : register callbacks when any config key or section changes, so I can trigger rolling updates or service restarts
* `VariableInterpolation` : resolve `${VAR}` and `${section.key}` placeholders at load time to keep secrets and endpoints DRY
* `ConfigVisualization`   : generate an interactive tree or graph of the merged config for documentation and review before deployment
* `DotNotationAccess`     : read and write values with `cfg.get("services.user.host")` and `cfg.set("services.user.port", 8080)`
* `NestedMerge`           : customize merging rules (e.g. append logging sinks but override replica counts) on deeply nested structures
* `ConflictReporting`     : detect contradictory overrides or circular references across layers and surface them as actionable errors
* `YAMLLoader`            : optionally import service definitions and global defaults from `.yml` files placed next to Helm charts
* `CustomCoercers`        : plug in my own parsers for durations, feature-flag enums, and IP address ranges
* `ProfilesSupport`       : define named profiles like `staging`, `canary`, `production` and switch via an env var or CLI flag
* `DefaultFallback`       : declare fallback values for any missing keys so my services never start with undefined settings
