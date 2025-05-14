# The Task

I am a DevOps engineer maintaining multi-environment deployments. I want a single library to load my production, staging, and local config in either JSON, INI or YAML formats; validate them; merge overrides; expand secrets from environment; and ship the final validated config to containerized services. I also need to automate QA checks by exporting JSON Schema and run interactive prompts in my bootstrap scripts.

# The Requirements

* `with_config` : Decorator-based Injection so bootstrap scripts and init functions get the right settings.
* `load_config` : JSON/INI/YAML Loader with format auto-detection.
* `_cache` : Caching Layer to skip redundant parsing in CI pipelines.
* `ValidationError` : Rich Error Reporting with file:line, section, key, expected vs. actual type, and suggested fixes.
* `ConfigManager.get` / `ConfigManager.set` : Programmatic Access API to merge overrides and hot-reload configs.
* `expand_env_vars` : Environment Variable Expansion for injecting secrets and tokens from CI.
* `validate_types` : Type Checking for integers, URLs, credentials.
* `export_json_schema` : JSON Schema Export so integration tests can validate configs before rollout.
* `prompt_missing` : Interactive Prompts in CLI bootstrap to fill missing secrets in secure environments.
* `load_yaml` (optional) : YAML Loader if config maintainers prefer `.yml` syntax for complex maps.

