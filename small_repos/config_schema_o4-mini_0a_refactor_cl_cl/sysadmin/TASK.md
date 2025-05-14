# The Task

I am a system administrator configuring dozens of servers. I want a standardized Python tool to parse host configuration from JSON, INI or YAML, validate IPs, ports, and credentials, expand environment overrides, cache the results, and programmatically push changes to Puppet or Ansible. I also need clear errors when the configuration is broken and the ability to export JSON Schema for policy review.

# The Requirements

* `with_config` : Decorator-based Injection into deployment scripts and management utilities.
* `load_config` : JSON/INI/YAML Loader with auto-discovered formats.
* `_cache` : Caching Layer keyed on file path and mtime to speed up batch operations.
* `ValidationError` : Rich Error Reporting: filename, line, section, key, expected vs. actual, suggested fix.
* `ConfigManager.get` / `ConfigManager.set` : Programmatic Access API for dynamic updates and serialization.
* `expand_env_vars` : Environment Variable Expansion for secrets and role-based overrides.
* `validate_types` : Type Checking for IP addresses, ports, booleans, and credential tokens.
* `export_json_schema` : JSON Schema Export for compliance audits and automated policy scanners.
* `prompt_missing` : Interactive Prompts in CLI when required values are missing.
* `load_yaml` (optional) : YAML Loader for more human-friendly inventory files.

