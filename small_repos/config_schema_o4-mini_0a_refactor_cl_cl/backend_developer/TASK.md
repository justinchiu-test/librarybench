# The Task

I am a backend developer working on a Python microservice framework. I want to be able to declare my service’s settings in JSON, INI or YAML, pull those settings into my classes and functions automatically, validate them at load time, enrich them with environment variables, and expose a live API for changing configuration on the fly. This code repository gives me decorators, loaders, validators, caching, and export tools so I can focus on business logic, not config plumbing.

# The Requirements

* `with_config` : Decorator-based Injection of validated config sections or keys into functions and class methods.
* `load_config` : JSON/INI/YAML Loader that auto-detects file format and parses into a unified Python dict.
* `_cache` : Caching Layer to store parsed and validated configs keyed by filepath and modification timestamp.
* `ValidationError` : Rich Error Reporting including filename, line number, section, key, expected vs. actual type, and suggested fixes.
* `ConfigManager.get` / `ConfigManager.set` : Programmatic Access API to query, update, and serialize configuration at runtime.
* `expand_env_vars` : Environment Variable Expansion for `${VAR}` or `$VAR` placeholders in string values.
* `validate_types` : Type Checking of loaded config values against declared Python or Pydantic types.
* `export_json_schema` : JSON Schema Export of the internal ConfigSchema definitions for external CI/CD validation tools.
* `prompt_missing` : Interactive Prompts on CLI to ask the developer for required but missing values.
* `load_yaml` (optional) : YAML Loader support via PyYAML or ruamel.yaml when a `.yaml` or `.yml` file is detected.

