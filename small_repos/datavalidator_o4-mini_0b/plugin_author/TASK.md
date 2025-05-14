# The Task

I am an open‐source contributor creating a plugin to enforce corporate policy on data inputs. I want to integrate seamlessly with the core validator, adding new rules and extension points without forking. This code repository offers a plugin API, schema hooks, and full access to error and logging pipelines.

# The Requirements

* `StrictMode` : Respect the host’s strict/permissive setting for my plugin rules.
* `OptionalFields` : Inspect schema optionality and override behavior when needed.
* `DataCoercion` : Hook into coercion pipeline to add custom type transformations.
* `FieldAliases` : Recognize field aliases defined in host schemas.
* `AggregatedErrorReporting` : Contribute additional error objects to the aggregated report.
* `TestDataGeneration` : Leverage schema‐based test data generator to validate plugin logic.
* `LoggingIntegration` : Emit structured log entries under a custom plugin namespace.
* `OpenAPI/JSONSchemaGeneration` : Augment host schema exports with plugin‐specific metadata.
* `PluginSystem` : Implement the standard plugin interface to register and configure my extension.
* `CustomValidators` : Provide a set of reusable validators (e.g. GDPR compliance checks) at field and schema levels.

