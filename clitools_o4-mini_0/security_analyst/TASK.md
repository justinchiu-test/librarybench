# The Task

I am a security analyst auditing our internal tooling and enforcing best practices. I want a CLI framework that ensures any tool I build comes with hardened signal handling, strict input validation, encrypted secrets, plugin audit hooks and retry-safe network calls. This code repository sets me up with secure defaults and extension points to enforce policy.

# The Requirements

* `bump_version` : Ensure each tool uses immutable, semantically versioned releases via git tags.
* `init_package` : Create a minimal pyproject.toml with security linting and dependency pinning.
* `publish_package` : Push only signed wheel files to our internal PyPI, with GPG verification.
* `register_hook` : Define audit and compliance hooks that run before and after each command invocation.
* `handle_signals` : Trap SIGINT/SIGTERM, revoke temporary credentials and log an “aborted for security” notice.
* `load_config` : Parse and merge YAML/TOML/JSON config with strict schema validation to prevent injection.
* `env_override` : Allow only whitelisted environment variable overrides with a custom “SEC_” prefix.
* `compute_default` : Generate unique session tokens or one-time salt values at runtime.
* `generate_docs` : Produce man pages with security usage guidelines embedded in command docs.
* `validate_input` : Enforce regex-based input rules, file permissions checks and custom range validators.
* `fetch_secret` : Integrate with AWS KMS, HashiCorp Vault or GPG to decrypt secrets on the fly.
* `retry_call` : Use jittered backoff for network calls to our SIEM or external APIs, with a max retry count.

