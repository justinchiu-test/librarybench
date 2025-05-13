# The Task

I am a QA Engineer verifying software builds across environments. I want an automated CLI-driven test runner that handles configuration, prompts for environment overrides, retries flaky tests, and generates test summaries. This code repository supplies a flexible flow engine for end-to-end test orchestration.

# The Requirements

* `load_config`         : Load test suite definitions and environment configs from JSON, YAML, TOML, or INI.  
* `run_dry_run`         : Simulate test execution plan without launching any tests.  
* `branch_flow`         : Branch further tests based on previous pass/fail exit codes.  
* `prompt_interactive`  : Prompt for browser selection, API endpoints, or custom test tags.  
* `secure_prompt`       : Mask credentials for test accounts or tokens and purge memory afterwards.  
* `retry`               : Retry individual tests or test groups with configurable backoff.  
* `context`             : Carry test artifacts, logs, and results between workflow steps.  
* `export_docs`         : Export the test plan to Markdown/HTML as a shareable QA report.  
* `register_hook`       : Hook into before-tests, after-each-test, on-failure, and on-complete events.  
* `validate_params`     : Validate environment names, browser versions, and tag patterns with clear errors.

