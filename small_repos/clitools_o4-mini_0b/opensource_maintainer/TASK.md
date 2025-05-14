# The Task

I am an open-source library maintainer who needs a bulletproof CLI foundation so contributors can add commands, docs and tests without reinventing the wheel. I want auto-versioning, plugin mechanisms, rich config support and built-in retries so all maintainer and contributor tasks are standardized. This code repository is the boilerplate that keeps everyone on the same page.

# The Requirements

* `bump_version` : Auto-increment semantic versions via git tags and generate changelog stubs.
* `init_package` : Create a comprehensive project scaffold (setup, CI config, tests folder).
* `publish_package` : One-step release to PyPI and GitHub Releases with checksums.
* `register_hook` : Expose pre- and post-command hook APIs so community plugins can extend the CLI.
* `handle_signals` : Standardized handling of SIGINT/SIGTERM plus cleanup log messages for all commands.
* `load_config` : Support for INI, JSON, YAML and TOML configs with prioritized merging.
* `env_override` : Worldwide users can override config via environment variables with a “OSS_” prefix.
* `compute_default` : Lazy defaults for things like build directories, timestamped docs output, or random demo tokens.
* `generate_docs` : Automatically export CLI reference as Markdown, HTML, reStructuredText and man pages for multi-format publishing.
* `validate_input` : Pluggable validators and coercers for argument types, ranges, regex patterns and file existence.
* `fetch_secret` : Provide hooks for keyring, Vault or GPG backends to safely manage contributor API tokens.
* `retry_call` : Built-in decorators for retrying flaky network calls to PyPI or external APIs with exponential backoff.

