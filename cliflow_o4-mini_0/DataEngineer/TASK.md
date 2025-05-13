# The Task

I am a Data Engineer. I want to build ETL pipelines that can be composed, tested, and scaled from the command line. This code repository helps me orchestrate data flows, switch output formats for downstream consumers, parallelize independent transformations, and integrate with existing tooling.

# The Requirements

* `set_renderer`           : Plug in alternative output renderers (color, plain text, JSON, Markdown) for logging and data previews.  
* `pipe`                   : Pass output of one ETL step as input to another, with automatic type conversion and serialization.  
* `parallelize`            : Run independent data transformations concurrently with a simple decorator.  
* `secure_input`           : Mask sensitive credentials (database passwords, API keys) and clear them from memory after use.  
* `translate`              : Internationalize status messages and transform metadata into user’s locale.  
* `export_workflow`        : Export defined ETL flows to Markdown or HTML docs for handoff and onboarding.  
* `load_config`            : Load default connection settings and pipeline profiles from JSON, YAML, TOML, or INI.  
* `env_inject`             : Map environment variables (e.g., AWS credentials, DB_HOST) to command parameters seamlessly.  
* `load_plugins`           : Dynamically discover and load external plugins for custom connectors or data sinks.  
* `redirect_io`            : Redirect stdin/stdout/stderr to files or custom handlers for audit logs and error reports.  
