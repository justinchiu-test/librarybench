# The Task

I am a data scientist who needs to package and distribute complex data-processing pipelines as standalone CLI tools. I want to ensure my users get clear documentation, valid configurations, and secure credentials for accessing data stores. This repository streamlines package management, config validation, secret injection, internationalized help, and robust cleanup if something goes wrong.

# The Requirements

* `<bump_version>` : Auto-increment the pipeline version in Git via tags for reproducibility.  
* `<gen_scaffold>` : Bootstrap new data CLI projects with `pyproject.toml` and test configurations.  
* `<publish_package>` : Push my analytics tools to PyPI or an internal artifactory with one command.  
* `<gen_config_schema>` : Derive JSON Schema/Cerberus definitions from my pipeline’s config interface.  
* `<validate_config>` : Preflight validate YAML/TOML/JSON/INI config files before running expensive ETL jobs.  
* `<format_help>` : Offer Markdown or colored terminal help so collaborators instantly understand usage.  
* `<load_translations>` : Keep UI strings in `.po/.mo` so global teams can read instructions in their language.  
* `<handle_signals>` : Gracefully handle keyboard interrupts, roll back partial data writes, and exit cleanly.  
* `<init_di>` : Declare dependencies (DB clients, ML models, message queues) and have them wired automatically.  
* `<parse_config_files>` : Load and merge multi-layered YAML and TOML configs with proper type coercion.  
* `<manage_secrets>` : Fetch database and API credentials securely from AWS KMS or HashiCorp Vault at runtime.  
* `<register_subcommands>` : Group ETL steps into subcommands (`extract`, `transform`, `load`) with shared flags.  
* `<env_override>` : Allow parameter overrides via environment variables to run in CI/CD without editing files.  
