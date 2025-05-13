# The Task

I am an IT Support Technician onboarding new employees. I want to script an interactive, reliable setup guide for workstations that prompts for role, applies correct policies, and logs actions. This code repository helps me build, test, and document the full setup flow.

# The Requirements

* `load_config`         : Load role-based defaults (software lists, network settings) from JSON, YAML, TOML, or INI.  
* `run_dry_run`         : Preview installations and configuration changes without touching the machine.  
* `branch_flow`         : Branch the installation process based on user’s department or OS.  
* `prompt_interactive`  : Ask for user name, department, software choices, and license keys.  
* `secure_prompt`       : Mask prompts for admin passwords or activation keys, clear memory afterwards.  
* `retry`               : Retry failed package installs or network mounts with exponential backoff.  
* `context`             : Store selected options, user details, and installation state across steps.  
* `export_docs`         : Export the complete onboarding workflow to Markdown/HTML for the IT handbook.  
* `register_hook`       : Hooks for pre-install checks, post-install notifications, and rollback on error.  
* `validate_params`     : Ensure valid usernames, department codes, and license keys, with helpful errors.

