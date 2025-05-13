# The Task

I am a Data Scientist orchestrating ETL pipelines and model training. I want to be able to compose interactive command-line workflows to validate data, run experiments, and deploy models reproducibly. This code repository provides a structured, testable, and documented CLI flow builder.

# The Requirements

* `load_config`         : Load data source credentials and model hyperparameters from JSON, YAML, TOML, or INI.  
* `run_dry_run`         : Simulate data ingestion and preprocessing steps without modifying any tables.  
* `branch_flow`         : Branch pipelines based on validation results or exit codes (e.g., skip training on bad data).  
* `prompt_interactive`  : Ask for dataset selection, parameter tweaks, or resource allocation (CPU vs GPU).  
* `secure_prompt`       : Mask prompts for database passwords and API tokens, then clear them after.  
* `retry`               : Apply retry/backoff to flaky data source reads or network calls.  
* `context`             : Pass DataFrame schemas, metrics, or artifacts between steps.  
* `export_docs`         : Generate Markdown/HTML docs describing the full ETL & training workflow.  
* `register_hook`       : Attach hooks to send Slack notifications pre-run, on success, or on failure.  
* `validate_params`     : Enforce correct data types, required fields, and value ranges for hyperparameters.

