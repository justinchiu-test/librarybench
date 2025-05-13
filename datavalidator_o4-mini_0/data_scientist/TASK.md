# The Task

I am a data scientist ingesting experimental results from multiple labs. I want to be able to standardize and validate heterogeneous CSV/JSON payloads before analysis. This code repository gives me schema‐driven validation, coercion, error aggregation, and synthetic data sampling to streamline preprocessing and testing.

# The Requirements

* `StrictMode` : Switch between forgiving parsing during exploration and strict checks in production.
* `OptionalFields` : Flag missing sensor readings as optional or required, with fallback strategies.
* `DataCoercion` : Auto‐convert strings, floats, or ints into the types my pipelines expect.
* `FieldAliases` : Map ambiguous column names (e.g. "temp", "temperature_C") to a unified schema.
* `AggregatedErrorReporting` : Collect and report all anomalies in a single pass with clear diagnostics.
* `TestDataGeneration` : Generate synthetic datasets to validate statistical analysis scripts.
* `LoggingIntegration` : Log every coercion and missing value handling event for reproducibility.
* `OpenAPI/JSONSchemaGeneration` : Output JSON Schema for data ingestion endpoints.
* `PluginSystem` : Add lab‐specific plugins (e.g. unit conversion rules).
* `CustomValidators` : Plug in bespoke checks (e.g. value distributions, outlier detectors).

