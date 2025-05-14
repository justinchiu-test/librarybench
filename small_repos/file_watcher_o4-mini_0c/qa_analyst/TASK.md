# The Task

I am a QA Analyst testing the stability of our front-end asset pipeline. I want to simulate file changes, track exactly what was modified, and replay events in batches to validate our watcher logic. This code repository helps me create reproducible test scenarios, tune filters for flaky artifacts, and feed results back into our test harness via CLI or REST.

# The Requirements

* `snapshotDiff`       : Take baseline snapshots of the asset directory and compute precise diffs after simulated changes.
* `fileHashComparison` : Validate file contents with MD5/SHA-256 hashes to ensure tests catch subtle content drifts.
* `dynamicFilterRules` : Adjust include/exclude rules mid-test to focus on specific file types or directories without restarting.
* `loggingSupport`     : Switch between verbose and minimal logging, choose structured output for parsing in our test framework.
* `configFileSupport`  : Define watcher parameters in external YAML/JSON/TOML so each test scenario is fully versioned.
* `gitignoreParsing`   : Leverage existing `.gitignore` to exclude build artifacts I don’t want to track during QA runs.
* `restfulAPI`         : Programmatically spin up watchers, inject test events, and retrieve results via HTTP calls.
* `eventBatching`      : Bundle related events into logical groups for bulk assertion checks in our test suite.
* `cliInterface`       : Use interactive CLI mode to manually trigger file operations and watch outcomes in real time.
* `hiddenFileFilter`   : Exclude dot-files so hidden metadata doesn’t pollute my test event streams.

