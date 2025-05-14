# The Task

I am an IoT Specialist ingesting sensor telemetry from thousands of devices. I want to validate each payload’s structure, enforce safe operating ranges, and drop faulty data early. This code repository is my gateway to schema-driven edge validation and custom plugin support.

# The Requirements

* `EnumConstraints` : Limit device_mode field to “sleep,” “active,” or “maintenance.”
* `ConditionalValidation` : Check battery_voltage only when power_source is “battery.”
* `DefaultValues` : Fill in missing firmware_version with the last known release.
* `RangeChecks` : Enforce temperature between -40 and 85 °C and humidity between 0 and 100%.
* `AsyncValidation` : Query a remote registry for device certificates before accepting payload.
* `SingleItemValidation` : Validate one telemetry record at a time to isolate faulty units.
* `OptionalFields` : Allow optional GPS coordinates but verify format when present.
* `StrictMode` : Strict mode on in production gateways to block out-of-spec devices.
* `PluginSystem` : Load plugins for unit conversions, data smoothing, or anomaly detection.
* `SchemaImportExport` : Define and distribute telemetry schemas in JSON or YAML to all edge nodes.
