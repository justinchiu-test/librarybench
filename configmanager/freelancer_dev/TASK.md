# The Task

I am a Freelance Full-Stack Developer building small to mid-sized web apps for clients.  
I want an easy, plug-and-play config manager that handles environment variables, multiple deployment targets, and secret storage without reinventing the wheel. This code repository will give me sensible defaults, a merge engine, plugin hooks, and built-in support for secrets and hot reloading in dev.

# The Requirements

* `merge_configs`         : Layer defaults, file-based settings, and environment variables with clear precedence.  
* `select_profile`        : Support named profiles for local, staging, and production deployments.  
* `export_env_vars`       : Emit `KEY=VALUE` pairs or directly inject into `os.environ` for Flask/Django processes.  
* `export_to_ini`         : Generate an INI snapshot for clients who need legacy INI-based tools.  
* `enable_hot_reload`     : Auto-reload config in development when I tweak files or environment settings.  
* `setup_logging`         : Log loads, merges, and validation errors to console and log files.  
* `fetch_secret`          : Integrate with Vault or AWS Secrets Manager to avoid committing credentials.  
* `cache_manager`         : Cache expensive operations like JSON schema validation or large list parsing.  
* `register_plugin`       : Add new secret stores or custom merge behaviors via a simple plugin API.  
* `set_precedence`        : Fine-tune which env vars can override client-provided JSON keys.  
