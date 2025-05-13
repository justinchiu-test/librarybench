# The Task

I am a Plugin Developer crafting extensions to integrate new services into our CLI.  
I want to be able to build, test, and distribute my plugins effortlessly while leveraging core CLIFlow features.  
This code repository streamlines plugin creation, discovery, lifecycle hooks, and publishing to a marketplace.

# The Requirements

* `generate_completion` : Auto-generate completion specs for the commands my plugin adds.  
* `export_workflow_docs` : Include my plugin steps in central workflow documentation.  
* `discover_plugins` : Let CLIFlow detect and register my plugin at runtime.  
* `redirect_io` : Handle custom input/output streams in my plugin actions.  
* `use_profile` : Access user-selected profiles from within plugin commands.  
* `serialize_data` : Read/write JSON, CSV, or YAML payloads in plugin logic.  
* `check_version` : Verify compatibility between plugin and CLIFlow core.  
* `manage_marketplace` : Publish and update my plugin on the community repository.  
* `register_hooks` : Provide pre-command, post-command, and on-error hooks for cleanup and metrics.  
* `run_tests` : Use the built-in testing harness for automated plugin validation and snapshots.

