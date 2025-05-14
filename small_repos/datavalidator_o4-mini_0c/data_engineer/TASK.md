# The Task

I am a Data Engineer responsible for building robust ETL pipelines. I want to be able to validate incoming JSON records in real time, enforce strict quality rules, and plug in custom business logic without rewriting core validation code. This code repository provides the schema-driven validation engine and extension hooks I need.

# The Requirements

* `EnumConstraints` : Restrict categorical fields (e.g., status, region) to a predefined set of allowed values.
* `ConditionalValidation` : Only validate shipment_date when order_status is “shipped,” otherwise skip that check.
* `DefaultValues` : Auto-populate missing timestamp and environment fields so pipelines don’t break on nulls.
* `RangeChecks` : Enforce min/max bounds on numeric metrics like quantity, price, and latency.
* `AsyncValidation` : Call out to an external service to verify customer IDs or credit limits before accepting a record.
* `SingleItemValidation` : Process one record at a time and return detailed pass/fail with error codes for logging.
* `OptionalFields` : Mark comment and discount_reason as optional but flag when present for audit.
* `StrictMode` : Fail fast on any unexpected or extra fields to catch schema drift early.
* `PluginSystem` : Drop in custom transform and enrich plugins (e.g., geo-lookup, currency conversion).
* `SchemaImportExport` : Save and load schema definitions as JSON or YAML so we can version and share them.

