# The Task

I am a Compliance Officer ensuring incoming data complies with GDPR and company policies. I want a centralized schema validation tool that flags disallowed fields, anonymizes PII, and can integrate with our audit logging. This code repository is my policy enforcement engine.

# The Requirements

* `EnumConstraints` : Enforce allowed values for data_retention_policy and user_consent_status.
* `ConditionalValidation` : Only require deletion_timestamp if user_consent_status is “revoked.”
* `DefaultValues` : Assign default policy_version when missing to track rule changes.
* `RangeChecks` : Validate age for minors (<16) and retention periods within legal bounds.
* `AsyncValidation` : Call an external anonymization service asynchronously for flagged PII fields.
* `SingleItemValidation` : Process each data deletion or export request individually with full trace logs.
* `OptionalFields` : Mark opt_out_reason as optional but record it when provided.
* `StrictMode` : Enforce strict schema checks in audit mode; switch to permissive for staging.
* `PluginSystem` : Integrate third-party compliance plugins for encryption, tokenization, and audit hooks.
* `SchemaImportExport` : Export final policy schemas to YAML for regulatory review and import updates via CI.
