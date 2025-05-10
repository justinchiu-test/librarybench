# The Task

I am a QA automation engineer building a CLI to run integration and regression test suites. I want grouped commands like “test run” and “test report,” configurable environments in YAML/TOML, interactive prompts for confirmations, graceful abort handling, plugin hooks for custom reporters, optional telemetry, abbreviations for quick runs, caching of test fixtures, standard flags, and auto-generated parsers. This repository gives me everything out of the box.

# The Requirements

* `register_subcommands`   : Group “test run”, “test smoke”, “test report” under a “test” namespace with shared options  
* `parse_config`           : Load test matrices and environment variables from INI/JSON/YAML/TOML with type coercion  
* `configure_prompt`       : Present test summaries and “Continue with rerun? [Y/n]” prompts using rich styles  
* `install_signal_handlers`: Catch SIGINT/SIGTERM to clean up test environments and print “Testing aborted”  
* `register_plugin_hooks`  : Hook in custom reporters or result processors before/after each test suite  
* `collect_telemetry`      : Optionally gather anonymized metrics on test durations and flags used for dashboards  
* `register_aliases`       : Allow abbreviations like “tr” for “test run” and prefix-based auto-completion  
* `cache_helper`           : Cache common fixtures or API authentication tokens in memory or on disk  
* `inject_common_flags`    : Automatically include --help, --version, --verbose/-v, --quiet on all test commands  
* `autobuild_parser`       : Generate argparse parsers from a declarative spec: typed args, choices, defaults, help text  
