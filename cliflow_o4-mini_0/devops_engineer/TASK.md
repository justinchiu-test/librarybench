# The Task

I am a DevOps Engineer automating infrastructure deployments. I want to be able to write modular, reliable CLI workflows that handle configuration, prompts, error recovery, and generate documentation for my team. This code repository gives me a framework to define, test, and export multi-step automation flows with built-in best practices.

# The Requirements

* `load_config`         : Load defaults and profile settings from JSON, YAML, TOML, or INI files.  
* `run_dry_run`         : Simulate command execution without side effects, showing intended actions.  
* `branch_flow`         : Branch workflows based on user input or command exit codes (e.g., deploy to staging vs production).  
* `prompt_interactive`  : Support yes/no, multi-choice (region, service), free-text, password, and numeric prompts in flowable sequences.  
* `secure_prompt`       : Mask sensitive prompts (API keys, tokens) and clear memory after use.  
* `retry`               : Decorators to retry failing operations (e.g., image push) with configurable backoff strategies.  
* `context`             : Carry state (credentials, target hosts, deployment flags) between steps with a shared context object.  
* `export_docs`         : Export defined flows to Markdown or HTML docs for team onboarding and runbooks.  
* `register_hook`       : Hookable lifecycle events (pre-command, post-command, on-error, on-exit) for custom logging and cleanup.  
* `validate_params`     : Built-in parameter validation, type checking, and user-friendly error messages for all CLI flags.

