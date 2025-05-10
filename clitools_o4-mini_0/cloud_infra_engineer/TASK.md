# The Task

I am a cloud infrastructure engineer automating the provisioning and monitoring of complex environments. I want a CLI scaffold that covers versioning, flexible configuration, secrets retrieval, reliable signal trapping and retry strategies—so I can build idempotent, well-documented tools in minutes. This code repository is my turnkey solution for every cloud automation project.

# The Requirements

* `bump_version` : Version infra modules automatically based on git tags, ensuring reproducible deployments.
* `init_package` : Generate robust pyproject.toml with cloud provider SDK dependencies locked.
* `publish_package` : Publish internal CLI tools to our private registry with one command.
* `register_hook` : Install hooks to run cost-reporting or compliance checks before and after infra changes.
* `handle_signals` : Gracefully catch SIGINT/SIGTERM to roll back half-applied stacks and log “Operation aborted.”
* `load_config` : Ingest multi-format configs (INI, JSON, YAML, TOML) for environments, regions and instance sizes.
* `env_override` : Expose all config via “CLOUD_” environment variables for pipeline overrides.
* `compute_default` : Auto-derive resource names using current timestamp or unique UUIDs.
* `generate_docs` : Export CLI usage to Markdown and man pages so teammates can self-serve the docs.
* `validate_input` : Validate CIDR blocks, port ranges, file paths and enforce type coercion.
* `fetch_secret` : Pull credentials and SSH keys from AWS KMS, HashiCorp Vault or the OS keyring.
* `retry_call` : Decorate API calls (Terraform, Cloud SDKs) with retry and backoff logic to handle throttling.
