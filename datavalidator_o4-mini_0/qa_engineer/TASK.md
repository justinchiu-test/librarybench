# The Task

I am a QA engineer tasked with end‐to‐end testing of our public APIs. I want to be able to automatically generate valid and invalid payloads, run them through the validator, and capture all error cases. This repo helps me define schemas once and then drive fuzzing, logging, and report generation.

# The Requirements

* `StrictMode` : Enforce strict mode for negative tests, permissive mode to validate edge cases.
* `OptionalFields` : Toggle optional/required flags to generate boundary payloads.
* `DataCoercion` : Test behavior when string numbers or booleans are coerced.
* `FieldAliases` : Validate both official and alias field names under test conditions.
* `AggregatedErrorReporting` : Collect every error with full path and expectation vs. actual.
* `TestDataGeneration` : Produce valid, invalid, minimal, and maximal payloads for fuzz testing.
* `LoggingIntegration` : Capture structured validation logs for test dashboards.
* `OpenAPI/JSONSchemaGeneration` : Drive contract tests against exported schema.
* `PluginSystem` : Inject test plugins that simulate downtime or latency rules.
* `CustomValidators` : Add domain‐specific failure conditions (e.g. payment limits).

