# The Task

I am a DevOps engineer who needs to build, deploy, and operate a suite of command-line tools for provisioning and maintaining infrastructure across multiple environments. I want to be able to scaffold, version, validate, secure, and internationalize my tooling with minimal boilerplate. This code repository gives me a one-stop CLI framework that handles release automation, config management, secrets, i18n, DI, and cleanup out of the box.

# The Requirements

* `<bump_version>` : Auto-bump versions via git tags so my release cycles are consistent.  
* `<gen_scaffold>` : Generate `setup.py` or `pyproject.toml` scaffolding for new CLI projects.  
* `<publish_package>` : Publish to PyPI or private indexes with a single command.  
* `<gen_config_schema>` : Build JSON Schema or Cerberus schemas from declarative config definitions.  
* `<validate_config>` : Validate YAML, TOML, JSON, or INI config files against the generated schema before execution.  
* `<format_help>` : Render plain-text, Markdown, or ANSI-colored help output with my company’s branding.  
* `<load_translations>` : Externalize all help strings, error messages, and prompts to `.po/.mo` files for localization.  
* `<handle_signals>` : Automatically catch SIGINT/SIGTERM, run registered cleanup tasks, and display friendly “aborted” messages.  
* `<init_di>` : Wire services, clients, and database connections via a lightweight dependency injection container at runtime.  
* `<parse_config_files>` : Parse YAML and TOML (in addition to INI/JSON) with schema merging and type coercion.  
* `<manage_secrets>` : Integrate with OS keyrings, AWS KMS, HashiCorp Vault, or GPG-encrypted files for securely storing and retrieving secrets.  
* `<register_subcommands>` : Organize commands into logical groups (“db migrate”, “net teardown”) with group-level flags and inheritance.  
* `<env_override>` : Bind configuration values to environment variables (with customizable prefixes) for 12-factor style overrides.  
