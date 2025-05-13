# The Task

I am a Security Analyst performing vulnerability scans and compliance checks. I want to script interactive audit workflows that handle secrets safely, retry on transient errors, and document results for audits. This code repository gives me a secure and auditable CLI flow toolkit.

# The Requirements

* `load_config`         : Load scan profiles and policy settings from JSON, YAML, TOML or INI files.  
* `run_dry_run`         : Preview scanning commands and affected hosts without executing them.  
* `branch_flow`         : Branch based on exit codes (e.g., high vs low severity findings) or user decisions.  
* `prompt_interactive`  : Ask for target selection, adjustment of scan intensity, or confirmation.  
* `secure_prompt`       : Mask credential prompts (SSH keys, API tokens) and ensure in-memory clearance.  
* `retry`               : Retry on transient network or authentication failures with backoff.  
* `context`             : Maintain scan results, host lists, and compliance state across steps.  
* `export_docs`         : Export audit workflows and results summary as Markdown/HTML for compliance.  
* `register_hook`       : Hook into pre-scan setup, post-scan reporting, on-error alerts, and final cleanup.  
* `validate_params`     : Validate target IPs, severity thresholds, and policy IDs with clear error messages.

