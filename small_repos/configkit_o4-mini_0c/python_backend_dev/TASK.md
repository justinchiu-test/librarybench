# The Task

I am a Python backend developer building a microservice platform. I want to load config from multiple file formats, validate my business‐critical settings at startup, and hot‐reload endpoints' settings during development. This repository gives me a single, consistent API for all my config needs.

# The Requirements

* `resolve_variables` : Interpolate environment variables and `${database.url}` references in nested dicts.  
* `load_toml`       : Import feature flags and dependency versions from TOML.  
* `load_yaml`       : Consume Kubernetes-style service templates in YAML.  
* `register_coercer`: Add coercers for `datetime`, `timedelta`, and custom `Enum` types.  
* `register_hook`   : Run pre–validation hooks to check API key formats, post–load hooks to mask secrets, and export hooks to generate JSON docs.  
* `watch_and_reload`: Auto-reload config modules when I tweak endpoints during local dev.  
* `merge_lists`     : Merge middleware lists incrementally (prepend debugging middleware in dev, append telemetry in prod).  
* `set_profile`     : Activate `dev`, `test`, or `prod` profiles via `PYTHON_ENV`.  
* `get`             : Use `cfg.get("service.cache.ttl")` to retrieve deeply nested settings in code.  
* `with_defaults`   : Supply default values for optional parameters (e.g., `max_connections=10` if unspecified).  
