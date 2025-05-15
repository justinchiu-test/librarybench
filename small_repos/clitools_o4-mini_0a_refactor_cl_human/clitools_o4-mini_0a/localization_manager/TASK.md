# The Task

I am a localization manager responsible for translating and maintaining CLI tools across multiple regions. I need a framework that cleanly separates text for translators, supports multiple help formats, and integrates with development workflows for versioning and releases.

# The Requirements

* `<bump_version>` : Keep translation CLI tools in sync by auto-bumping versions via Git tags.  
* `<gen_scaffold>` : Scaffold new CLI repos with `pyproject.toml` that include i18n hooks.  
* `<publish_package>` : Publish translated CLI packages to PyPI or private feeds quickly.  
* `<gen_config_schema>` : Generate JSON/Cerberus schemas for CLI config files to catch locale-specific validation issues.  
* `<validate_config>` : Pre-validate localized config files (YAML, TOML, JSON, INI) against schemas.  
* `<format_help>` : Produce help in plain-text, Markdown, or ANSI-colored form, tailored per locale.  
* `<load_translations>` : Externalize all strings to `.po/.mo` files; support gettext workflows and automated merges.  
* `<handle_signals>` : Ensure translators see friendly “aborted” messages if they cancel a long export/import.  
* `<init_di>` : Manage dependencies (translation memory, glossaries, MT engines) through a DI container.  
* `<parse_config_files>` : Parse and merge locale configs in YAML and TOML with correct type coercion.  
* `<manage_secrets>` : Safely handle API keys for translation services via keyrings, Vault, or GPG.  
* `<register_subcommands>` : Organize commands into `extract`, `translate`, `review`, `publish` groups with shared flags.  
* `<env_override>` : Let translators override endpoints and feature flags via environment variables for testing.  
