# The Task

I am a data engineer responsible for the integrity and evolution of our data APIs. I want to be able to track and manage changes in API schemas, validate incoming payloads asynchronously when necessary, and transform or redact data before it reaches downstream systems. This code repository provides a unified schema-driven validation, transformation, and versioning framework to power our data pipelines.

# The Requirements

* `SchemaDiffTool` : Visualize or compute the delta between two schema definitions to support change tracking.  
* `ErrorLocalization` : Translate error messages into multiple languages via pluggable i18n backends.  
* `PluginArchitecture` : Discover and register rule and transformer plugins via entry points for community extensions.  
* `AsyncValidationSupport` : Async-capable rules for I/O bound checks (e.g. DB lookups) using asyncio.  
* `ProfileBasedRules` : Enable rule sets to vary by “profile” (e.g. signup vs. admin API) and switch context at runtime.  
* `CoreDateTimeValidation` : Date parsing (ISO, custom formats), time zone normalization, and min/max date checks.  
* `SchemaInheritance` : Define child schemas inheriting and overriding parent schemas to avoid duplication.  
* `SchemaVersioning` : Assign version IDs to schemas, manage migrations, and validate against historical versions.  
* `TransformationPipeline` : Chain transforms (e.g. trim, lowercase, date→timestamp) on valid values before output.  
* `SecureFieldMasking` : Automatic redaction or hashing of sensitive fields (e.g. SSN, credit card) in logs and reports.  
