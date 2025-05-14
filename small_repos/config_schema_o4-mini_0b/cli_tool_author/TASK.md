# The Task

I am a Python library author building a CLI tool that needs user‐configurable behavior. I want a robust configuration backend that supports inheritance for user, project, and global levels, lazy loading of optional plugin configs, multiple validation modes for “interactive” vs. “CI” runs, INI/JSON loading, .env support, environment interpolation, and a plugin system so third parties can add new file types or post-processing steps. This code repository is my turn-key solution.

# The Requirements

* `inherit_schema`               : Let project overrides extend or override global defaults.  
* `lazy_load_section`            : Only parse plugin configurations when the plugin is actually enabled.  
* `set_validation_context`       : Validate more strictly under CI than in interactive mode.  
* `load_config`                  : Seamlessly load JSON or INI user settings.  
* `load_env_file`                : Merge in a `.env` file from the working directory.  
* `register_plugin`              : Expose hooks so plugin authors can add new loaders, validators, or commands.  
* `apply_defaults`               : Supply default logging levels, timeouts, etc., when users omit them.  
* `compose_schemas`              : Combine core, plugin, and user schemas into one final config.  
* `expand_env_vars`              : Expand `$HOME` and other env lookups in command templates.  
* `prompt_for_missing`           : Prompt the user for required fields they haven’t set yet.  
