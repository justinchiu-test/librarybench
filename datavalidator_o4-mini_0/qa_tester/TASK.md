# The Task

I am a QA Tester in charge of automating data validation tests for our microservices. I want to write declarative test cases against schemas, feed in edge-case samples, and generate detailed reports on failures. This code repository supplies a validation harness and reporting plugins.

# The Requirements

* `EnumConstraints` : Test that status codes only allow “pending,” “approved,” or “rejected.”
* `ConditionalValidation` : Verify discount_code rules only apply when coupon_applied is true.
* `DefaultValues` : Confirm missing fields like region default properly under various locales.
* `RangeChecks` : Assert numeric limits for inventory_level, response_time, and file_size checks.
* `AsyncValidation` : Simulate slow external validation (e.g., tax ID lookup) and handle timeouts gracefully.
* `SingleItemValidation` : Run single-message validation runs to pinpoint failures down to one object.
* `OptionalFields` : Check optional notes and attachments behave as expected when omitted or null.
* `StrictMode` : Toggle strict mode in tests to detect both schema violations and unexpected extras.
* `PluginSystem` : Extend the validator with custom assertions, like “no personally identifiable info.”
* `SchemaImportExport` : Version control schema snapshots in JSON/YAML to replay historical tests.
