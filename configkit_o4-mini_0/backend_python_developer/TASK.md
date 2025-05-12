# The Task

I am a backend Python developer building a suite of microservices. I want to be able to layer configuration from defaults, files, environment, and command line; catch bad overrides early; and even tweak settings on the fly during local development. This code repository gives me a rock-solid, extensible configuration system that does exactly that.

# The Requirements

* `DefaultFallback` : specify built-in defaults for every key so missing or optional settings get auto-filled
* `TOMLLoader` : load service-specific config from TOML files in `/etc/myapp` and `~/myapp/.config`
* `EnvLoader` : import overrides from environment variables using a `MYAPP_` prefix and map them to nested keys
* `ArgvLoader` : parse any additional command-line flags via `argparse` and treat them as the highest-precedence layer
* `ConflictReporting` : detect and error out when two layers define mutually contradictory values or circular references
* `NestedMerge` : merge nested dictionaries for things like `database.replicas` but override entire arrays for `middleware.plugins`
* `CustomCoercers` : plug in my own functions to coerce strings into `timedelta`, `ipaddress`, and custom enum types
* `CLIConfigGenerator` : auto-generate a `myservice --host --port --log-level` CLI so I never hand-write boilerplate flags
* `ConfigWatcher` : register a callback that restarts only the logging subsystem if `log.level` changes at runtime
* `HotReload` : watch the TOML and YAML config files so local code reloads and re-validates on every save without a restart

