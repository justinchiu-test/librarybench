# The Task

I am a backend developer building a microservice admin CLI for migrations, health checks, and debugging. I want top-notch version control, configuration schemas, custom help themes, secret management, and localization so my team can deploy and operate services consistently worldwide.

# The Requirements

* `<bump_version>` : Automate service CLI version bumps using Git tags.  
* `<gen_scaffold>` : Scaffold `setup.py`/`pyproject.toml` with predefined entry points.  
* `<publish_package>` : Release to PyPI or our private index in one step.  
* `<gen_config_schema>` : Generate config schemas from declarative definitions (JSON/Cerberus).  
* `<validate_config>` : Validate JSON, INI, YAML, and TOML settings before connecting to upstream systems.  
* `<format_help>` : Provide plain-text, Markdown, or ANSI-colored help with custom templates for internal branding.  
* `<load_translations>` : Externalize UI strings and error messages to `.po/.mo` files for localization.  
* `<handle_signals>` : Capture SIGINT/SIGTERM, run cleanup (close DB connections), and show “aborted” notices.  
* `<init_di>` : Declare and resolve dependencies (Redis, Postgres, Kafka) via a lightweight DI container.  
* `<parse_config_files>` : Merge multiple config sources (YAML, TOML, INI, JSON) with type coercion.  
* `<manage_secrets>` : Securely load credentials from OS keyring, AWS KMS, or GPG at runtime.  
* `<register_subcommands>` : Group admin commands under namespaces (`migrate`, `seed`, `status`) with shared flags.  
* `<env_override>` : Override config values via env vars (with project‐specific prefixes) for Docker and K8s.  
