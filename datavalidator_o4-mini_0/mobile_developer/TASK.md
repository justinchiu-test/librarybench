# The Task

I am a mobile developer building a cross‐platform app. I want to be able to safely parse server responses into my view models. This code repository offers a lightweight, schema‐based validator that guards against crashes, coaxes missing fields, and produces logs for remote debugging.

# The Requirements

* `StrictMode` : Easily toggle between forgiving and strict runtime checks in development or CI builds.
* `OptionalFields` : Define which JSON keys can be missing without crashing the app.
* `DataCoercion` : Convert numeric strings or booleans into native types for UI bindings.
* `FieldAliases` : Accept both snake_case and camelCase to support multiple backend teams.
* `AggregatedErrorReporting` : Gather all parsing issues and show user‐friendly errors on a debug screen.
* `TestDataGeneration` : Create mock responses to simulate every combination of fields.
* `LoggingIntegration` : Send structured validation logs to remote analytics when errors occur.
* `OpenAPI/JSONSchemaGeneration` : Validate requests against generated mobile‐friendly JSON Schemas.
* `PluginSystem` : Add feature‐flag plugins to enable or disable new experimental fields.
* `CustomValidators` : Inject custom rules (e.g. image URL reachability checks) per screen.

