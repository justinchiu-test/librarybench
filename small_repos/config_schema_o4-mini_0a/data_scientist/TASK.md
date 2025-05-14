# The Task

I am a data scientist building ML pipelines. I want a flexible config system I can use in Jupyter notebooks and production batch jobs that auto-loads parameters from JSON, INI or YAML files, casts them to the right types, overrides via environment variables, and lets me explore or tweak them interactively. I’d also like to export the schema to JSON for reproducibility reports.

# The Requirements

* `with_config` : Decorator-based Injection into model-training functions and evaluation scripts.
* `load_config` : JSON/INI/YAML Loader that picks up experiment settings.
* `_cache` : Caching Layer so repeated notebook runs are faster.
* `ValidationError` : Rich Error Reporting with file, line, section, key context and suggestions.
* `ConfigManager.get` / `ConfigManager.set` : Programmatic Access API to inspect or tweak hyperparameters.
* `expand_env_vars` : Environment Variable Expansion to pull credentials for data sources.
* `validate_types` : Type Checking for floats, ints, lists, and custom types (e.g., numpy arrays).
* `export_json_schema` : JSON Schema Export for CI reproducibility checks and audit trails.
* `prompt_missing` : Interactive Prompts in notebook cells or CLI to request missing parameters.
* `load_yaml` (optional) : YAML Loader for users who prefer YAML’s readability for nested structures.

