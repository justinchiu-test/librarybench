# The Task

I am a QA engineer writing integration tests for a complex distributed app. I want a reliable config library to load test parameters from JSON, INI or YAML, validate them fully, and expose a simple API so my test harness can tweak or introspect settings. When tests fail due to bad config, I need precise error messages and a JSON Schema export so our CI pipeline can lint new test configs automatically.

# The Requirements

* `with_config` : Decorator-based Injection into test fixtures and helper methods.
* `load_config` : JSON/INI/YAML Loader with automatic detection.
* `_cache` : Caching Layer to avoid redundant parsing in parallel test runs.
* `ValidationError` : Rich Error Reporting: file, line, section, key, expected vs. actual type, and hints.
* `ConfigManager.get` / `ConfigManager.set` : Programmatic Access API to feed test cases and rewrite configs.
* `expand_env_vars` : Environment Variable Expansion to inject dynamic endpoints from CI environments.
* `validate_types` : Type Checking to catch mis-typed thresholds or endpoint URLs.
* `export_json_schema` : JSON Schema Export so we can integrate config checks into our CI lint stage.
* `prompt_missing` : Interactive Prompts if a required test parameter is missing in local dev runs.
* `load_yaml` (optional) : YAML Loader in case test teams prefer YAML fixtures.
