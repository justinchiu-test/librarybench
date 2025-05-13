# The Task

I am a developer building developer-friendly CLI tools that rely on configurable behavior. I want a configuration library that supports custom formats, interactive prompts, secret handling, and self-documenting outputs, so my users get rock-solid tools out of the box. This code repository gives me everything I need to manage CLI configurations elegantly.

# The Requirements

* `secret_manager_integration` : Let end users fetch or rotate secrets via AWS KMS or Vault commands inside the CLI.
* `json_schema_support` : Offer JSON Schema export and runtime validation for plugin settings.
* `deprecation_warnings` : Warn users when they use deprecated flags or config keys in the CLI.
* `config_merger` : Merge default flags, config files, and environment variables with user-definable precedence.
* `interactive_cli` : Provide interactive prompts for missing inputs (e.g., API endpoints, tokens) during CLI execution.
* `list_merge_strategies` : Support append, replace, and unique-merge strategies for lists of subcommands or plugins.
* `documentation_gen` : Generate Markdown and HTML docs for CLI config options directly from schema and comments.
* `custom_format_loaders` : Allow plugin authors to register new file-format loaders (TOML, XML) or URL-based configs.
* `secret_decryption` : Automatically detect and decrypt encrypted secrets (AES or base64) in user configs.
* `error_reporting` : Surface rich error messages with file, line number, and context so end users can fix config issues immediately.
