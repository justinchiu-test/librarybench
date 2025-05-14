# The Task

I am a backend engineer responsible for our user‐management microservice. I want to be able to enforce consistent, correct, and well‐documented payloads across all endpoints. This code repository provides a flexible validation framework that adapts to both legacy clients and new integrations, while generating schema docs and runtime logs.

# The Requirements

* `StrictMode` : Toggle strict versus permissive validation behavior to protect new endpoints.
* `OptionalFields` : Mark user profile fields (e.g. middleName, phoneNumber) as optional or required with custom defaults.
* `DataCoercion` : Automatic type casting (e.g. string "42" → integer 42 for user age).
* `FieldAliases` : Map external JSON keys (e.g. "first_name") to internal model attributes (`firstName`).
* `AggregatedErrorReporting` : Collect all validation errors per request, including field paths and human‐readable messages.
* `TestDataGeneration` : Produce realistic user objects for unit tests and load tests.
* `LoggingIntegration` : Emit structured logs on every validation event (info, warning, error) for observability and auditing.
* `OpenAPI/JSONSchemaGeneration` : Export endpoint schemas to OpenAPI v3 for our REST docs.
* `PluginSystem` : Extend validation with company‐wide rules (e.g. enforce corporate email domains).
* `CustomValidators` : Register custom functions at the field level (e.g. validate password strength or unique username).

